import gnupg

gpg = gnupg.GPG(homedir='/home/gmulhearn/gpghome')

input_data = gpg.gen_key_input(key_type="RSA", key_length=1024)

key = gpg.gen_key(input_data)

ascii_armored_public_keys = gpg.export_keys(key)
ascii_armored_private_keys = gpg.export_keys(key, True)
with open('mykeyfile.asc', 'w') as f:
    f.write(ascii_armored_public_keys)
    f.write(ascii_armored_private_keys)