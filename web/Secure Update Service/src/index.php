<?php
chdir(sys_get_temp_dir());

$algorithm = "sha1";
$config_file = "last_update.xml";

function download($filename)
{
    if (!file_exists($filename)) {
        die("file $filename not found");
    }

    header("Content-Disposition: attachment; filename=" . basename($filename));
    header("Content-Type: application/octet-stream");
    header("Content-Length: " . filesize($filename));
    header("Expires: 0");
    header("Cache-Control: must-revalidate");
    header("Pragma: public");
    readfile($filename);
    exit();
}

function is_filename_valid($filename)
{
    return preg_match('/^[^\/.g-j][^.g-j]*$/i', $filename);
}

function is_signature_valid($filename)
{
    global $algorithm;

    try {
        $root = new SimpleXMLElement(file_get_contents($filename));
        $computed = hash_hmac($algorithm, (string) $root->data, getenv("KEY"));

        return $computed === (string) $root->signature;
    } finally {
    }

    return false;
}

function reset_config()
{
    global $algorithm, $config_file;

    $command = "sh update.sh";

    $xml = new SimpleXMLElement("<root/>");
    $xml->addChild("data", $command);
    $xml->addChild("signature", hash_hmac($algorithm, $command, getenv("KEY")));

    $xml->saveXML($config_file);

    copy(__DIR__ . "/update.sh", "update.sh");
    copy("/flag.txt", "flag.txt");
}

if (!file_exists($config_file)) {
    reset_config();
}

if (isset($_GET["reset"])) {
    reset_config();
    die("reset");
}

if (isset($_GET["source"])) {
    download(__FILE__);
}

if (isset($_GET["download"])) {
    download($config_file);
}

$message = null;
$is_error = false;

function handle_submission()
{
    global $message, $algorithm, $config_file, $is_error;

    $is_error = true;

    if (!isset($_FILES["update-config"])) {
        return;
    }

    $filename = $_FILES["update-config"]["full_path"];
    if (!is_filename_valid($filename)) {
        $message = "The filename $filename is not valid";
        return;
    }

    $init_hash = md5_file($_FILES["update-config"]["tmp_name"]);

    move_uploaded_file($_FILES["update-config"]["tmp_name"], $filename);

    if (!is_signature_valid($filename)) {
        unlink($filename);
        $message = "The file does not have a valid signature.";
        return;
    }

    if ($init_hash !== md5_file($filename)) {
        unlink($filename);
        $message = "The file got corrupted. Bad disk?";
        return;
    }

    copy($filename, $config_file);
    unlink($filename);

    $is_error = false;
    $message = "File was uploaded successfully!";
}

function deploy($filename)
{
    global $message, $is_error;

    $config = simplexml_load_file($filename);

    $is_error = false;
    $message = shell_exec($config->data);
}

if (isset($_GET["deploy"])) {
    deploy($config_file);
} else {
    try {
        handle_submission();
    } catch (Exception $e) {
        $message =
            "An error occurred while processing the file upload: " .
            $e->getMessage();
    }
}
?>
<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Secure Update Service</title>
        <link
            rel="stylesheet"
            href="https://getbootstrap.com/1.4.0/assets/css/bootstrap.min.css"
        />
        <style type="text/css">
            body {
                padding-top: 60px;
            }
        </style>
    </head>
    <body>
        <div class="topbar">
            <div class="fill">
                <div class="container">
                    <p class="brand">Secure Update Service</p>
                    <ul class="nav">
                        <li><a href="/?source">Source code</a></li>
                    </ul>
                </div>
            </div>
        </div>

        <div class="container">
            <div class="hero-unit">
                <h1>Secure Update Service</h1>
                <p>
                    Welcome to the Secure Update Service (SUS). You can deploy
                    firmware update configuration to all the machines in the lab with this
                    utility. All uploads will be validated.
                </p>
                <form
                    action="/?upload"
                    method="post"
                    enctype="multipart/form-data"
                >
                    <div class="clearfix">
                        <label for="update-config">Update configuration</label>
                        <div class="input">
                            <input type="file" name="update-config" class="input-file" />
                        </div>
                    </div>
                    <div class="actions">
                        <p>
                            <button class="btn primary large" type="submit">
                                Upload new version
                            </button>
                        </p>
                        <p><a class="btn large" href="/?download">Download current update configuration</a></p>
                        <p><a class="btn large" href="/?reset">Reset to default update configuration</a></p>
                        <p><a class="btn large" href="/?deploy">Deploy current update configuration</a></p>
                    </div>
                </form>
                <?php if (!empty($message)) {
                    $css_class = $is_error ? "error" : "success";
                    $exclamation = $is_error ? "Oops" : "Hooray";
                    echo "<div class='alert-message $css_class'><strong>$exclamation!</strong> " .
                        htmlspecialchars($message) .
                        "</div>";
                } ?>
            </div>
        </div>
    </body>
</html>
