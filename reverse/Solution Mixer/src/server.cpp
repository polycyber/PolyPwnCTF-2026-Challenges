#include <QTcpServer>
#include <QTcpSocket>
#include <QCoreApplication>
#include <QHostAddress>
#include <QFile>
#include <QTextStream>
#include <QElapsedTimer>
#include <QDateTime>
#include <QDebug>
#include <cstring>
#include <cstdlib>
#include <ctime>
#include <cmath>
#include <algorithm>
#include <tuple>
#include <unistd.h>
#include <pwd.h>
#include <openssl/aes.h>
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/sha.h>
#include <QByteArray>

class SolutionServer : public QObject {
    Q_OBJECT

private:
    QTcpServer* server;
    QString flag;
    int currentFlagIndex;
    QStringList encryptedExceptionalSolutions;
    
    int getFlagIndex(int step) {
        return (step % flag.length());
    }
    
    int getFlagBit(int position, int bitNumber) {
        if (position < 0 || position >= flag.length()) return 0;
        char c = flag[position].toLatin1();
        return (c >> bitNumber) & 1;
    }
    
    int computeSolutionHash(const QString& sol1, const QString& sol2) {
        QString combined = sol1 + sol2;
        int hash = 0;
        for (int i = 0; i < combined.length(); ++i) {
            hash = ((hash << 5) - hash) + combined[i].unicode();
            hash = hash & hash;
        }
        return abs(hash);
    }
    
    std::tuple<double, double, double> getReactionProperties(const QString& sol1, const QString& sol2) {
        int hash = computeSolutionHash(sol1, sol2);
        double volumeChange = 0.90 + ((hash % 30) / 100.0);
        double vaporRate = 0.05 + ((hash % 20) / 100.0);
        double reactionHeat = (hash % 50) - 25;
        return std::make_tuple(volumeChange, vaporRate, reactionHeat);
    }
    
    QByteArray deriveAESKey(const QString& flag) {
        QByteArray flagBytes = flag.toUtf8();
        unsigned char hash[SHA256_DIGEST_LENGTH];
        SHA256_CTX sha256;
        SHA256_Init(&sha256);
        SHA256_Update(&sha256, flagBytes.data(), flagBytes.length());
        SHA256_Final(hash, &sha256);
        return QByteArray(reinterpret_cast<const char*>(hash), SHA256_DIGEST_LENGTH);
    }
    
    QByteArray deriveIV(const QString& flag) {
        QByteArray flagBytes = flag.toUtf8();
        QByteArray salted = flagBytes + "IV_SALT_FOR_EXCEPTIONAL_SOLUTIONS";
        unsigned char hash[SHA256_DIGEST_LENGTH];
        SHA256_CTX sha256;
        SHA256_Init(&sha256);
        SHA256_Update(&sha256, salted.data(), salted.length());
        SHA256_Final(hash, &sha256);
        return QByteArray(reinterpret_cast<const char*>(hash), 16);
    }
    
    QByteArray encryptAES(const QString& plaintext, const QString& key) {
        QByteArray keyBytes = deriveAESKey(key);
        QByteArray iv = deriveIV(key);
        QByteArray plaintextBytes = plaintext.toUtf8();
        
        int padding = 16 - (plaintextBytes.length() % 16);
        plaintextBytes.append(padding, static_cast<char>(padding));
        
        EVP_CIPHER_CTX* ctx = EVP_CIPHER_CTX_new();
        if (!ctx) return QByteArray();
        
        if (EVP_EncryptInit_ex(ctx, EVP_aes_256_cbc(), nullptr, 
                               reinterpret_cast<const unsigned char*>(keyBytes.data()),
                               reinterpret_cast<const unsigned char*>(iv.data())) != 1) {
            EVP_CIPHER_CTX_free(ctx);
            return QByteArray();
        }
        
        QByteArray ciphertext;
        ciphertext.resize(plaintextBytes.length() + AES_BLOCK_SIZE);
        int len = 0;
        int ciphertextLen = 0;
        
        if (EVP_EncryptUpdate(ctx, 
                              reinterpret_cast<unsigned char*>(ciphertext.data()), &len,
                              reinterpret_cast<const unsigned char*>(plaintextBytes.data()),
                              plaintextBytes.length()) != 1) {
            EVP_CIPHER_CTX_free(ctx);
            return QByteArray();
        }
        ciphertextLen = len;
        
        if (EVP_EncryptFinal_ex(ctx,
                                reinterpret_cast<unsigned char*>(ciphertext.data()) + len,
                                &len) != 1) {
            EVP_CIPHER_CTX_free(ctx);
            return QByteArray();
        }
        ciphertextLen += len;
        ciphertext.resize(ciphertextLen);
        
        EVP_CIPHER_CTX_free(ctx);
        return ciphertext.toHex().toUpper();
    }
    
    QString decryptAES(const QString& ciphertextHex, const QString& key) {
        QByteArray ciphertext = QByteArray::fromHex(ciphertextHex.toLatin1());
        QByteArray keyBytes = deriveAESKey(key);
        QByteArray iv = deriveIV(key);
        
        EVP_CIPHER_CTX* ctx = EVP_CIPHER_CTX_new();
        if (!ctx) return QString();
        
        if (EVP_DecryptInit_ex(ctx, EVP_aes_256_cbc(), nullptr,
                               reinterpret_cast<const unsigned char*>(keyBytes.data()),
                               reinterpret_cast<const unsigned char*>(iv.data())) != 1) {
            EVP_CIPHER_CTX_free(ctx);
            return QString();
        }
        
        QByteArray plaintext;
        plaintext.resize(ciphertext.length() + AES_BLOCK_SIZE);
        int len = 0;
        int plaintextLen = 0;
        
        if (EVP_DecryptUpdate(ctx,
                              reinterpret_cast<unsigned char*>(plaintext.data()), &len,
                              reinterpret_cast<const unsigned char*>(ciphertext.data()),
                              ciphertext.length()) != 1) {
            EVP_CIPHER_CTX_free(ctx);
            return QString();
        }
        plaintextLen = len;
        
        if (EVP_DecryptFinal_ex(ctx,
                                reinterpret_cast<unsigned char*>(plaintext.data()) + len,
                                &len) != 1) {
            EVP_CIPHER_CTX_free(ctx);
            return QString();
        }
        plaintextLen += len;
        
        if (plaintextLen > 0 && plaintext[plaintextLen - 1] > 0 && 
            plaintext[plaintextLen - 1] <= 16) {
            int padding = static_cast<unsigned char>(plaintext[plaintextLen - 1]);
            plaintextLen -= padding;
        }
        plaintext.resize(plaintextLen);
        
        EVP_CIPHER_CTX_free(ctx);
        return QString::fromUtf8(plaintext);
    }

    void simulateReactionTime(int step, const QString& sol1, const QString& sol2, 
                              double qty1, double qty2) {
        int idx = getFlagIndex(step);
        int timeBits = (getFlagBit(idx, 1) << 1) | getFlagBit(idx, 2);
        usleep(timeBits * 1000000 + qty1 + qty2);
    }

    double computeTemperature(int step, const QString& sol1, const QString& sol2) {
        int idx = getFlagIndex(step);
        auto [volumeChange, vaporRate, reactionHeat] = getReactionProperties(sol1, sol2);
        int solutionHash = computeSolutionHash(sol1, sol2);
        int tempBase = 20 + (solutionHash % 30);
        tempBase += static_cast<int>(reactionHeat * 0.3);
        int tempBit = getFlagBit(idx, 0);
        return tempBase + (tempBit * 0.5);
    }
    
    double computeVaporQuantity(const QString& sol1, const QString& sol2, double totalInput) {
        auto [volumeChange, vaporRate, reactionHeat] = getReactionProperties(sol1, sol2);
        double vaporEfficiency = vaporRate;
        return totalInput * vaporEfficiency;
    }
    
    double computeLiquidQuantity(const QString& sol1, const QString& sol2, 
                                 double totalInput, double vaporQty) {
        auto [volumeChange, vaporRate, reactionHeat] = getReactionProperties(sol1, sol2);
        double volumeFactor = volumeChange;
        return (totalInput - vaporQty) * volumeFactor;
    }
    
    double computePressure(double vaporQty, double temperature) {
        double basePressure = 1.0 + (vaporQty / 100.0);
        double tempEffect = (temperature - 20.0) * 0.01;
        return basePressure * (1.0 + tempEffect);
    }
    
    int computeColor(int step) {
        int idx = getFlagIndex(step);
        
        int color = rand() & 0xffffff;
        
        int r = (color >> 16) & 0xff;
        int g = (color >> 8) & 0xff;
        int b = color & 0xff;
        
        int bit4 = getFlagBit(idx, 3);
        int bit5 = getFlagBit(idx, 4);
        int bit6 = getFlagBit(idx, 5);
        
        r = (r & 0x7f) | (bit4 << 7);
        g = (g & 0x7f) | (bit5 << 7);
        b = (b & 0x7f) | (bit6 << 7);
        
        color = (r << 16) | (g << 8) | b;
        
        return color;
    }
    
    QString getFlagBitsHex() {
        QString bits;
        for (int i = 0; i < flag.length(); ++i) {
            int bit7 = getFlagBit(i, 6);
            bits += QString::number(bit7);
        }
        
        int padding = (4 - (bits.length() % 4)) % 4;
        for (int i = 0; i < padding; ++i) {
            bits = "0" + bits;
        }
        
        QString hex;
        for (int i = 0; i < bits.length(); i += 4) {
            QString nibble = bits.mid(i, 4);
            int value = 0;
            for (int j = 0; j < 4; ++j) {
                if (nibble[j] == '1') {
                    value |= (1 << (3 - j));
                }
            }
            hex += QString::number(value, 16).toUpper();
        }
        
        return hex;
    }

    QString computeCharacteristics(int step, const QString& sol1, const QString& sol2, 
                                   double qty1, double qty2) {
        double totalInput = qty1 + qty2;
        
        double temperature = computeTemperature(step, sol1, sol2);
        double vaporQty = computeVaporQuantity(sol1, sol2, totalInput);
        double liquidQty = computeLiquidQuantity(sol1, sol2, totalInput, vaporQty);
        double pressure = computePressure(vaporQty, temperature);
        int color = computeColor(step);
        
        return QString("RESULT|%1|%2|%3|%4|%5")
            .arg(temperature, 0, 'f', 1)
            .arg(liquidQty, 0, 'f', 1)
            .arg(vaporQty, 0, 'f', 1)
            .arg(pressure, 0, 'f', 1)
            .arg(color);
    }
    
    void loadEncryptedSolutions() {
        QFile file("exceptional_solutions.enc");
        if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
            qDebug() << "Failed to open exceptional_solutions.enc, creating default";
            QStringList rawExceptional = QStringList() 
                << "Solution Alpha - Propriétés exceptionnelles"
                << "Solution Beta - Réactivité maximale"
                << "Solution Gamma - Stabilité parfaite"
                << "Solution Delta - Potentiel énergétique élevé";
            
            encryptedExceptionalSolutions.clear();
            for (const QString& sol : rawExceptional) {
                QByteArray encrypted = encryptAES(sol, flag);
                encryptedExceptionalSolutions << QString::fromLatin1(encrypted);
            }
            saveEncryptedSolutions();
            return;
        }
        
        QTextStream in(&file);
        QStringList lines;
        while (!in.atEnd()) {
            QString line = in.readLine().trimmed();
            if (!line.isEmpty()) {
                lines << line;
            }
        }
        file.close();
        
        encryptedExceptionalSolutions = lines;
    }
    
    void saveEncryptedSolutions() {
        QFile file("exceptional_solutions.enc");
        if (!file.open(QIODevice::WriteOnly | QIODevice::Text)) {
            qDebug() << "Failed to save exceptional_solutions.enc";
            return;
        }
        
        QTextStream out(&file);
        for (const QString& encrypted : encryptedExceptionalSolutions) {
            out << encrypted << "\n";
        }
        file.close();
    }
    
    QString decryptExceptionalSolutions() {
        QStringList decrypted;
        for (const QString& encryptedHex : encryptedExceptionalSolutions) {
            QString decryptedSol = decryptAES(encryptedHex, flag);
            if (decryptedSol.isEmpty()) {
                decrypted << "Erreur de décryptage";
            } else {
                decrypted << decryptedSol;
            }
        }
        return "DECRYPTED|" + decrypted.join("|");
    }
    
    QString getCurrentUsername() {
        struct passwd* pw = getpwuid(geteuid());
        if (pw && pw->pw_name) {
            return QString::fromLocal8Bit(pw->pw_name);
        }
        const char* user = getenv("USER");
        if (!user) {
            user = getenv("USERNAME");
        }
        if (user) {
            return QString::fromLocal8Bit(user);
        }
        return QString();
    }
    
    void encryptAndSaveSolutions(const QStringList& solutions) {
        encryptedExceptionalSolutions.clear();
        for (const QString& sol : solutions) {
            QByteArray encrypted = encryptAES(sol, flag);
            encryptedExceptionalSolutions << QString::fromLatin1(encrypted);
        }
        saveEncryptedSolutions();
    }

private slots:
    void handleNewConnection() {
        QTcpSocket* clientSocket = server->nextPendingConnection();
        if (!clientSocket) return;
        
        connect(clientSocket, &QTcpSocket::readyRead, this, [this, clientSocket]() {
            QByteArray data = clientSocket->readAll();
            QString message = QString::fromUtf8(data).trimmed();
            
            QStringList messages = message.split("\n", Qt::SkipEmptyParts);
            
            for (const QString& msg : messages) {
                QStringList parts = msg.split("|");
                
                if (parts.isEmpty()) continue;
                
                QString command = parts[0];
            
            if (command == "MIX") {
                if (parts.size() >= 6) {
                    QString sol1 = parts[1];
                    QString sol2 = parts[2];
                    double qty1 = parts[3].toDouble();
                    double qty2 = parts[4].toDouble();
                    int step = parts[5].toInt();
                    
                    QString result = computeCharacteristics(step, sol1, sol2, qty1, qty2);
                    simulateReactionTime(step, sol1, sol2, qty1, qty2);
                    clientSocket->write((result + "\n").toUtf8());
                    clientSocket->flush();
                }
            } else if (command == "DECRYPT") {
                    QString result = decryptExceptionalSolutions();
                    clientSocket->write((result + "\n").toUtf8());
                    clientSocket->flush();
                } else if (command == "ENCRYPT_SAVE") {
                    QString username = getCurrentUsername();
                    if (username != "not-implemented-yet") {
                        clientSocket->write("ERROR|L'option d'écriture n'est pas encore implémentée\n");
                        clientSocket->flush();
                    } else {
                        QStringList solutions;
                        for (int i = 1; i < parts.size(); ++i) {
                            solutions << parts[i];
                        }
                        encryptAndSaveSolutions(solutions);
                        clientSocket->write("SAVED\n");
                        clientSocket->flush();
                    }
                } else if (command == "GET_ENCRYPTED") {
                    QString flagBitsHex = getFlagBitsHex();
                    QString result = "ENCRYPTED|" + flagBitsHex + "|" + encryptedExceptionalSolutions.join("|");
                    clientSocket->write((result + "\n").toUtf8());
                    clientSocket->flush();
                }
            }
        });
        
        connect(clientSocket, &QTcpSocket::disconnected, clientSocket, &QTcpSocket::deleteLater);
    }

public:
    SolutionServer(QObject* parent = nullptr) : QObject(parent) {
        QFile flagFile("flag.txt");
        if (flagFile.open(QIODevice::ReadOnly | QIODevice::Text)) {
            QTextStream in(&flagFile);
            flag = in.readAll().trimmed();
            flagFile.close();
        } else {
            qDebug() << "Failed to open flag.txt";
            QCoreApplication::exit(1);
            exit(1);
        }
        currentFlagIndex = 0;
        
        loadEncryptedSolutions();
        
        server = new QTcpServer(this);
        if (!server->listen(QHostAddress::Any, 34512)) {
            qDebug() << "Failed to start server:" << server->errorString();
            QCoreApplication::exit(1);
        }
        
        connect(server, &QTcpServer::newConnection, this, &SolutionServer::handleNewConnection);
        qDebug() << "Server listening on port:" << server->serverPort();
    }
};

int main(int argc, char *argv[]) {
    QCoreApplication app(argc, argv);
    
    SolutionServer server;
    
    return app.exec();
}

#include "server.moc"

