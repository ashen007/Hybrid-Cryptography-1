import os, sys, zipfile
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5


# Define Public and Private key names!

# Sender's public key:
pubKey = "A_PublicKey.pem"
# Receiver's private key:
priKey = "B_PrivateKey.pem"

# File name to decrypt
f_name = ""

def usage():
    print "python decipherPy.py <File_Name>"


def hashVerification(pubKey_fname, f_name):
    # Generating decrypted file's SHA-256

    h = SHA256.new()
    h.update(open(f_name, "r").read())

    # Reading PublicKey to check Signature with

    keyPair = RSA.importKey(open(pubKey_fname, "r").read())
    keyVerifier = PKCS1_v1_5.new(keyPair.publickey())

    # If Signature is right, prints SHA-256. Otherwise states that the file is not authentic

    if keyVerifier.verify(h, open(f_name.split('.')[0] + ".sig", "r").read()):
        print "The signature is authentic."
        print "SHA-256 -> %s" % h.hexdigest()
    else:
        print "The signature is not authentic."


def keyReader(privKey_fname, f_name):
    # Reading PrivateKey to decipher Symmetric key used

    keyPair = RSA.importKey(open(privKey_fname, "r").read())
    keyDecipher = PKCS1_OAEP.new(keyPair)

    # Reading iv (initializing vector) used to encrypt and saving Symmetric key used to 'k'

    f = open(f_name.split('.')[0] + ".key", "r")
    iv = f.read(16)
    k = keyDecipher.decrypt(f.read())

    return k, iv


def decipher(keyA_fname, keyB_fname, f_name):
    # Getting Symmetric key used and iv value generated at encryption process

    k, iv = keyReader(keyB_fname, f_name)

    # Deciphering the initial information and saving it to file with no extension

    keyDecipher = AES.new(k, AES.MODE_CFB, iv)
    bin = open(f_name + ".bin", "rb").read()
    f = open(f_name.split('.')[0], "wb")
    f.write(keyDecipher.decrypt(bin))
    f.close()

    # Running a Signature verification

    hashVerification(keyA_fname, f_name.split('.')[0])


def auxFilesUnzip(all):
    # Opening the input file

    f = zipfile.ZipFile(all + ".all", "r")

    # Extracting all of its files

    f.extractall()


def cleanUp(sig, key, bin, all):
    # Removing all of the files created, except for the final deciphered file

    os.remove(sig)
    os.remove(key)
    os.remove(bin)
    os.remove(all)

def checkFiles(f_name, pubKey, priKey, first_run):
    # Checking for decrypting file's existence and access

    if first_run and (not os.path.isfile(f_name + ".all") or not os.access(f_name + ".all", os.R_OK)):
        print "Invalid file to decrypt. Aborting..."
        sys.exit(1)

    elif not first_run:
        # Checking if all of the necessary files exist and are accessible

        if not os.path.isfile(f_name + ".sig") or not os.access(f_name + ".sig", os.R_OK):
            print "Invalid *.sig file. Aborting..."
            sys.exit(2)
        if not os.path.isfile(f_name + ".key") or not os.access(f_name + ".key", os.R_OK):
            print "Invalid *.key file. Aborting..."
            sys.exit(3)
        if not os.path.isfile(f_name + ".bin") or not os.access(f_name + ".bin", os.R_OK):
            print "Invalid *.bin file. Aborting..."
            sys.exit(4)

        # Checking if in case of output file's existence, it is writable

        if os.path.isfile(f_name) and not os.access(f_name, os.W_OK):
            print "Can't create output file. Aborting..."
            sys.exit(5)

    # Checking for public key's existence and access

    if not os.path.isfile(pubKey) or not os.access(pubKey, os.R_OK):
        print "Invalid public key file. Aborting..."
        sys.exit(6)

    # Checking for private key's existence and access

    if not os.path.isfile(priKey) or not os.access(priKey, os.R_OK):
        print "Invalid private key file. Aborting..."
        sys.exit(7)


# Gathering encrypting file name

if len(sys.argv) > 2:
    usage()
elif len(sys.argv) == 1:
    print "File name:"
    f_name = raw_input(">>> ")
else:
    f_name = sys.argv[1]

# Gathering keys names

if pubKey == "":
    print "Sender's public key file name:"
    pubKey = raw_input(">>> ")
if priKey == "":
    print "Receiver's private key file name:"
    priKey = raw_input(">>> ")


f_name = f_name.split('.')[0]
checkFiles(f_name, pubKey, priKey, True)
auxFilesUnzip(f_name)
checkFiles(f_name, pubKey, priKey, False)
decipher(pubKey, priKey, f_name)
cleanUp(f_name + ".sig", f_name + ".key", f_name + ".bin", f_name + ".all")