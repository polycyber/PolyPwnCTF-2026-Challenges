#include <QApplication>
#include <QMainWindow>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QWidget>
#include <QPushButton>
#include <QComboBox>
#include <QLabel>
#include <QTextEdit>
#include <QGroupBox>
#include <QProgressBar>
#include <QTimer>
#include <QMessageBox>
#include <QListWidget>
#include <QStringList>
#include <QDoubleSpinBox>
#include <QFormLayout>
#include <QTcpSocket>
#include <QHostAddress>
#include <QAbstractSocket>
#include <QByteArray>
#include <QLineEdit>
#include <QSpinBox>
#include <cstdlib>

class SolutionMixer : public QMainWindow {
    Q_OBJECT

private:
    QStringList baseSolutions;
    QTcpSocket* socket;
    QString serverHost;
    quint16 serverPort;
    int currentStep;
    
    QComboBox* solution1Combo;
    QComboBox* solution2Combo;
    QDoubleSpinBox* quantity1Spin;
    QDoubleSpinBox* quantity2Spin;
    QPushButton* mixButton;
    QPushButton* decryptButton;
    QTextEdit* resultsDisplay;
    QLabel* statusLabel;
    QProgressBar* progressBar;
    QTextEdit* exceptionalTextEdit;
    QLabel* colorCircle;
    bool isDecrypted;
    QLineEdit* serverAddressEdit;
    QSpinBox* serverPortSpin;
    QPushButton* connectButton;

private slots:
    void onConnected() {
        statusLabel->setText(QString("Connecté au serveur %1:%2").arg(serverHost).arg(serverPort));
        connectButton->setEnabled(true);
        connectButton->setText("Déconnecter");
        socket->write("GET_ENCRYPTED\n");
        socket->flush();
    }
    
    void onDisconnected() {
        statusLabel->setText("Déconnecté du serveur");
        connectButton->setEnabled(true);
        connectButton->setText("Se connecter");
    }
    
    void onReadyRead() {
        QByteArray data = socket->readAll();
        QString message = QString::fromUtf8(data).trimmed();
        QStringList parts = message.split("|");
        
        if (parts.isEmpty()) return;
        
        QString command = parts[0];
        
        if (command == "RESULT") {
            if (parts.size() >= 6) {
                double temperature = parts[1].toDouble();
                double liquidQty = parts[2].toDouble();
                double vaporQty = parts[3].toDouble();
                double pressure = parts[4].toDouble();
                int color = parts[5].toInt();
                
                QString colorHex = QString("#%1").arg(color, 6, 16, QChar('0')).toUpper();
                
                colorCircle->setText("");
                QString styleSheet = QString("QLabel { background-color: %1; border: 2px solid #333; }").arg(colorHex);
                colorCircle->setStyleSheet(styleSheet);
                
                QString result = QString(
                    "=== Caractéristiques de la solution résultante ===\n"
                    "Température: %1°C\n"
                    "Quantité (liquide): %2 mL\n"
                    "Quantité (vapeur): %3 mL\n"
                    "Pression (vapeur): %4 atm\n"
                    "==========================================\n"
                ).arg(temperature, 0, 'f', 1)
                 .arg(liquidQty, 0, 'f', 1)
                 .arg(vaporQty, 0, 'f', 1)
                 .arg(pressure, 0, 'f', 1);
                
                resultsDisplay->setPlainText(result);
                statusLabel->setText(QString("Mélange terminé (étape %1)").arg(currentStep));
                progressBar->setVisible(false);
                mixButton->setEnabled(true);
            }
        } else if (command == "DECRYPTED") {
            QStringList solutions;
            for (int i = 1; i < parts.size(); ++i) {
                solutions << parts[i];
            }
            exceptionalTextEdit->setPlainText(solutions.join("\n"));
            exceptionalTextEdit->setReadOnly(false);
            isDecrypted = true;
            decryptButton->setText("Encrypter et Sauvegarder");
            statusLabel->setText("Solutions exceptionnelles décryptées");
        } else if (command == "ENCRYPTED") {
            if (parts.size() >= 2) {
                QString flagBitsHex = parts[1];
                QStringList encrypted;
                for (int i = 2; i < parts.size(); ++i) {
                    encrypted << parts[i];
                }
                QString displayText = flagBitsHex + "\n" + encrypted.join("\n");
                exceptionalTextEdit->setPlainText(displayText);
            } else {
                exceptionalTextEdit->setPlainText("");
            }
            isDecrypted = false;
            decryptButton->setText("Décrypter");
        } else if (command == "SAVED") {
            statusLabel->setText("Solutions exceptionnelles sauvegardées");
            exceptionalTextEdit->setReadOnly(true);
            isDecrypted = false;
            decryptButton->setText("Décrypter");
            socket->write("GET_ENCRYPTED\n");
            socket->flush();
        } else if (command == "ERROR") {
            QString errorMsg = parts.size() > 1 ? parts[1] : "Erreur inconnue";
            statusLabel->setText("Erreur: " + errorMsg);
            QMessageBox::warning(this, "Erreur", errorMsg);
            
            if (!isDecrypted) {
                if (exceptionalTextEdit->toPlainText().isEmpty()) {
                    socket->write("GET_ENCRYPTED\n");
                    socket->flush();
                }
                isDecrypted = false;
                decryptButton->setText("Décrypter");
            }
        }
    }
    
    void onError(QAbstractSocket::SocketError error) {
        Q_UNUSED(error);
        statusLabel->setText("Erreur de connexion au serveur");
        connectButton->setEnabled(true);
        connectButton->setText("Se connecter");
        QMessageBox::warning(this, "Erreur", 
            QString("Impossible de se connecter au serveur %1:%2.\n"
                    "Assurez-vous que le serveur est en cours d'exécution.")
                .arg(serverHost).arg(serverPort));
    }

public:
    SolutionMixer(const QString& initialHost = QString(), quint16 initialPort = 0, QWidget *parent = nullptr) 
        : QMainWindow(parent), currentStep(0), isDecrypted(false) {
        baseSolutions << "Acide chlorhydrique"
                      << "Hydroxyde de sodium"
                      << "Eau distillée"
                      << "Peroxyde d'hydrogène"
                      << "Acide sulfurique"
                      << "Nitrate d'argent"
                      << "Chlorure de sodium"
                      << "Sulfate de cuivre";
        
        if (!initialHost.isEmpty()) {
            serverHost = initialHost;
        } else {
            serverHost = getenv("SERVER_HOST");
            if (serverHost.isEmpty()) {
                serverHost = "localhost";
            }
        }
        
        if (initialPort > 0) {
            serverPort = initialPort;
        } else {
            const char* portEnv = getenv("SERVER_PORT");
            if (portEnv) {
                serverPort = QString::fromLatin1(portEnv).toUShort();
            } else {
                serverPort = 34512;
            }
        }
        
        socket = new QTcpSocket(this);
        connect(socket, &QTcpSocket::connected, this, &SolutionMixer::onConnected);
        connect(socket, &QTcpSocket::disconnected, this, &SolutionMixer::onDisconnected);
        connect(socket, &QTcpSocket::readyRead, this, &SolutionMixer::onReadyRead);
        connect(socket, &QAbstractSocket::errorOccurred, this, &SolutionMixer::onError);
        
        setupUI();
        
        serverAddressEdit->setText(serverHost);
        serverPortSpin->setValue(serverPort);
        
        if (!initialHost.isEmpty() || initialPort > 0) {
            QTimer::singleShot(100, this, &SolutionMixer::connectToServer);
        }
    }
    
    void connectToServer() {
        if (socket->state() == QAbstractSocket::ConnectedState) {
            socket->disconnectFromHost();
            return;
        }
        
        serverHost = serverAddressEdit->text().trimmed();
        if (serverHost.isEmpty()) {
            serverHost = "localhost";
            serverAddressEdit->setText(serverHost);
        }
        
        serverPort = static_cast<quint16>(serverPortSpin->value());
        
        statusLabel->setText(QString("Connexion à %1:%2...").arg(serverHost).arg(serverPort));
        connectButton->setEnabled(false);
        socket->connectToHost(serverHost, serverPort);
    }
    
    void setupUI() {
        QWidget* centralWidget = new QWidget(this);
        setCentralWidget(centralWidget);
        QVBoxLayout* mainLayout = new QVBoxLayout(centralWidget);
        
        QLabel* title = new QLabel("Logiciel de Test de Combinaisons d'Éléments", this);
        title->setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;");
        mainLayout->addWidget(title);
        
        QGroupBox* connectionGroup = new QGroupBox("Connexion au Serveur", this);
        QHBoxLayout* connectionLayout = new QHBoxLayout(connectionGroup);
        
        QLabel* addressLabel = new QLabel("Adresse:", this);
        serverAddressEdit = new QLineEdit(this);
        serverAddressEdit->setText(serverHost);
        serverAddressEdit->setPlaceholderText("localhost ou IP");
        
        QLabel* portLabel = new QLabel("Port:", this);
        serverPortSpin = new QSpinBox(this);
        serverPortSpin->setRange(1, 65535);
        serverPortSpin->setValue(serverPort);
        
        connectButton = new QPushButton("Se connecter", this);
        connectButton->setStyleSheet("padding: 5px;");
        
        connectionLayout->addWidget(addressLabel);
        connectionLayout->addWidget(serverAddressEdit);
        connectionLayout->addWidget(portLabel);
        connectionLayout->addWidget(serverPortSpin);
        connectionLayout->addWidget(connectButton);
        connectionLayout->addStretch();
        
        mainLayout->addWidget(connectionGroup);
        
        QGroupBox* selectionGroup = new QGroupBox("Sélection des Solutions", this);
        QFormLayout* formLayout = new QFormLayout(selectionGroup);
        
        QHBoxLayout* sol1Layout = new QHBoxLayout();
        solution1Combo = new QComboBox(this);
        solution1Combo->addItems(baseSolutions);
        quantity1Spin = new QDoubleSpinBox(this);
        quantity1Spin->setRange(1.0, 1000.0);
        quantity1Spin->setValue(100.0);
        quantity1Spin->setSuffix(" mL");
        quantity1Spin->setDecimals(1);
        sol1Layout->addWidget(solution1Combo);
        sol1Layout->addWidget(quantity1Spin);
        formLayout->addRow("Solution 1:", sol1Layout);
        
        QHBoxLayout* sol2Layout = new QHBoxLayout();
        solution2Combo = new QComboBox(this);
        solution2Combo->addItems(baseSolutions);
        quantity2Spin = new QDoubleSpinBox(this);
        quantity2Spin->setRange(1.0, 1000.0);
        quantity2Spin->setValue(100.0);
        quantity2Spin->setSuffix(" mL");
        quantity2Spin->setDecimals(1);
        sol2Layout->addWidget(solution2Combo);
        sol2Layout->addWidget(quantity2Spin);
        formLayout->addRow("Solution 2:", sol2Layout);
        
        mixButton = new QPushButton("Mélanger les Solutions", this);
        mixButton->setStyleSheet("padding: 10px; font-size: 14px;");
        formLayout->addRow(mixButton);
        
        mainLayout->addWidget(selectionGroup);
        
        progressBar = new QProgressBar(this);
        progressBar->setRange(0, 0);
        progressBar->setVisible(false);
        mainLayout->addWidget(progressBar);
        
        QGroupBox* resultsGroup = new QGroupBox("Résultats de l'Analyse", this);
        QVBoxLayout* resultsLayout = new QVBoxLayout(resultsGroup);
        
        resultsDisplay = new QTextEdit(this);
        resultsDisplay->setReadOnly(true);
        resultsDisplay->setMinimumHeight(200);
        resultsLayout->addWidget(resultsDisplay);
        
        QHBoxLayout* colorLayout = new QHBoxLayout();
        QLabel* colorLabel = new QLabel("Couleur de la solution résultante :", this);
        colorCircle = new QLabel(this);
        colorCircle->setMinimumSize(30, 30);
        colorCircle->setMaximumSize(30, 30);
        colorCircle->setStyleSheet(
            "QLabel { background-color: #FFFFFF; border: 2px solid #333; }"
        );
        colorCircle->setText("");
        colorLayout->addWidget(colorLabel);
        colorLayout->addWidget(colorCircle);
        colorLayout->addStretch();
        resultsLayout->addLayout(colorLayout);
        
        mainLayout->addWidget(resultsGroup);
        
        QGroupBox* exceptionalGroup = new QGroupBox("Solutions Exceptionnelles (Protégées)", this);
        QVBoxLayout* exceptionalLayout = new QVBoxLayout(exceptionalGroup);
        
        exceptionalTextEdit = new QTextEdit(this);
        exceptionalTextEdit->setReadOnly(true);
        exceptionalTextEdit->setMaximumHeight(150);
        exceptionalLayout->addWidget(exceptionalTextEdit);
        
        decryptButton = new QPushButton("Décrypter", this);
        decryptButton->setStyleSheet("padding: 8px; font-size: 12px;");
        exceptionalLayout->addWidget(decryptButton);
        
        mainLayout->addWidget(exceptionalGroup);
        
        statusLabel = new QLabel("Connexion au serveur...", this);
        statusLabel->setStyleSheet("padding: 5px;");
        mainLayout->addWidget(statusLabel);
        
        connect(mixButton, &QPushButton::clicked, this, &SolutionMixer::onMixClicked);
        connect(decryptButton, &QPushButton::clicked, this, &SolutionMixer::onDecryptClicked);
        connect(connectButton, &QPushButton::clicked, this, &SolutionMixer::connectToServer);
        
        setWindowTitle("Système de Test de Combinaisons - Version 2.1.3");
        resize(800, 750);
    }

private slots:
    void onDecryptClicked() {
        if (!socket->isOpen()) {
            QMessageBox::warning(this, "Erreur", "Non connecté au serveur");
            return;
        }
        
        if (!isDecrypted) {
            socket->write("DECRYPT\n");
            socket->flush();
        } else {
            QString text = exceptionalTextEdit->toPlainText();
            QStringList solutions = text.split("\n", Qt::SkipEmptyParts);
            
            if (solutions.isEmpty()) {
                QMessageBox::warning(this, "Erreur", "Aucune solution à sauvegarder");
                return;
            }
            
            QString request = "ENCRYPT_SAVE|" + solutions.join("|") + "\n";
            socket->write(request.toUtf8());
            socket->flush();
        }
    }
    
    void onMixClicked() {
        if (!socket->isOpen()) {
            QMessageBox::warning(this, "Erreur", "Non connecté au serveur");
            return;
        }
        
        if (solution1Combo->currentText() == solution2Combo->currentText()) {
            QMessageBox::warning(this, "Erreur", "Veuillez sélectionner deux solutions différentes.");
            return;
        }
        
        double qty1 = quantity1Spin->value();
        double qty2 = quantity2Spin->value();
        
        if (qty1 <= 0 || qty2 <= 0) {
            QMessageBox::warning(this, "Erreur", "Les quantités doivent être supérieures à 0.");
            return;
        }
        
        statusLabel->setText("Calcul en cours...");
        progressBar->setVisible(true);
        mixButton->setEnabled(false);
        
        QString request = QString("MIX|%1|%2|%3|%4|%5\n")
            .arg(solution1Combo->currentText())
            .arg(solution2Combo->currentText())
            .arg(qty1)
            .arg(qty2)
            .arg(currentStep++);
        
        socket->write(request.toUtf8());
        socket->flush();
    }
};

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    
    QString serverHost;
    quint16 serverPort = 0;
    
    QStringList args = app.arguments();
    for (int i = 1; i < args.size(); ++i) {
        if (args[i] == "--host" || args[i] == "-h") {
            if (i + 1 < args.size()) {
                serverHost = args[++i];
            }
        } else if (args[i] == "--port" || args[i] == "-p") {
            if (i + 1 < args.size()) {
                bool ok;
                serverPort = args[++i].toUShort(&ok);
                if (!ok) {
                    qWarning() << "Invalid port number, using default 34512";
                    serverPort = 0;
                }
            }
        } else if (args[i] == "--help") {
            qInfo() << "Usage:" << args[0] << "[--host|-h <address>] [--port|-p <port>]";
            qInfo() << "  --host, -h    Server hostname or IP address (default: localhost)";
            qInfo() << "  --port, -p    Server port (default: 34512)";
            qInfo() << "  --help        Show this help message";
            return 0;
        }
    }
    
    SolutionMixer window(serverHost, serverPort);
    window.show();
    
    return app.exec();
}

#include "client.moc"
