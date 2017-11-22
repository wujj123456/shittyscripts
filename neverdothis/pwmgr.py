#!/usr/bin/python

import sys, os, string, shutil
import getpass, traceback, hashlib
import platform
from Tkinter import Tk
from Crypto.Random import random
from Crypto.Hash import HMAC
from Crypto.Cipher import Blowfish
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto import Random
from struct import pack

saltLength = 16

def usage():
	print '''valid operations:
	pwmgr createlevel <level> - create encryption level <level>
	pwmgr removelevel <level> - delete encryption level <level>
	pwmgr resetlevel <level> - reset the password of <level>
	pwmgr add <level> <id> - add a password for <id> under <level>
	pwmgr delete <level> <id> - delete <id> under <level>
	pwmgr query <level> <id> - query password of <id> under <level>
	pwmgr rename <level> <id> <new_id> - change name of <id>
	pwmgr list <level> - list all ids under <level>
	pwmgr search <level> <keyword> - search <keyword> under <level>'''
        sys.exit(-1)

def checkArgLength(arg, l):
        if len(arg) != l:
                usage()

def getDirname(level):
        h = hashlib.sha512()
        h.update(level)
        return h.hexdigest()

# change to sha256?
def enhancePass(salt, pw):
        return PBKDF2(pw, salt, 32, 5000)

def genRandomPass(len, pattern):
        # http://stackoverflow.com/questions/2257441/python-random-string-generation-with-upper-case-letters-and-digits
        ret = ''.join(random.choice(pattern) for x in range(len))
        return ret

def genRandomPassHelper():
        pattern = string.ascii_letters+string.digits+r'''~!@#$%^&*()_+-=|[]{}:";<>'?,./'''
        length = 16
        
        s = raw_input('Password length? [16] ')
        if s != '':
                length = int(s)
        s = raw_input('Generate password using default pattern? [Y/n] ')
        if s.lower() == 'y' or s == '':
                return genRandomPass(length, pattern)
        else:
                pattern = ''
        print 'Customizing password pattern...'
        s = raw_input('Include a-z? [Y/n] ')
        if s.lower() == 'y' or s == '':
                pattern += string.ascii_lowercase
        s = raw_input('Include A-Z? [Y/n] ')
        if s.lower() == 'y' or s == '':
                pattern += string.ascii_uppercase
        s = raw_input('Include 0-9? [Y/n] ')
        if s.lower() == 'y' or s == '':
                pattern += string.digits
        s = raw_input('Type allowed punctuations: ')
        pattern += s
        return genRandomPass(length, pattern)

def readEncryptedFile(level):
        # http://desk.stinkpot.org:8080/tricks/index.php/2007/08/read-or-write-a-python-dict-tofrom-a-text-file/
        f = open(getDirname(level) + '/.data', 'rb')
        r = f.read()
        f.close()
        return r

# deprecated
def decryptStringBlowfish(r, passwd):
        sys.exit("Deprecated function!")
        bs = Blowfish.block_size
        iv = r[1:bs+1]
        cipher = Blowfish.new(passwd, Blowfish.MODE_CBC, iv)
        msg = cipher.decrypt(r[1:])[bs:-int(r[0])]
        return eval(msg)

def decryptStringAES(r, passwd):
        bs = AES.block_size
        iv = r[:bs]
        cipher = AES.new(passwd, AES.MODE_CBC, iv)
        msg = cipher.decrypt(r)[bs:].rstrip('\0')
        return eval(msg)

# deprecated
def readPassFileBlowfish(level, passwd):
        sys.exit("Deprecated function!")
        r = readEncryptedFile(level)
        if r == '':
                return dict()
        return decryptStringBlowfish(r, passwd)

def readPassFileAES(level, passwd):
        r = readEncryptedFile(level)
        if r == '':
                return dict()
        return decryptStringAES(r, passwd)

def readPassFile(level, passwd):
        return readPassFileAES(level, passwd)

def writeEncryptedFile(r, level):
        f = open(getDirname(level) + '/.data', 'wb')
        f.write(r)
        f.close()

# deprecated
def writePassFileBlowfish(dictData, level, passwd):
        sys.exit("Deprecated function!")
        bs = Blowfish.block_size
        iv = Random.new().read(bs)
        cipher = Blowfish.new(passwd, Blowfish.MODE_CBC, iv)
        msg = str(dictData)
        plen = bs - divmod(len(msg),bs)[1]
        padding = [plen]*plen
        padding = pack('b'*plen, *padding)
        writeEncryptedFile(str(plen) + iv + cipher.encrypt(msg + padding), level)

def writePassFileAES(dictData, level, passwd):
        bs = AES.block_size
        iv = Random.new().read(bs)
        cipher = AES.new(passwd, AES.MODE_CBC, iv)
        msg = str(dictData)
        plen = bs - divmod(len(msg),bs)[1]
        padding = [0]*plen
        padding = pack('b'*plen, *padding)
        writeEncryptedFile(iv + cipher.encrypt(msg + padding), level)
        
# storage format: <1 byte padding length><8 byte iv><encrypted data>
def writePassFile(dictData, level, passwd):
        writePassFileAES(dictData, level, passwd)

# deprecated
def blowfishToAES(level, passwd):
        sys.exit("Deprecated function!")
        r = readEncryptedFile(level)
        if r == '':
                return dict()
        d = decryptStringBlowfish(r, passwd)
        print d
        writePassFileAES(d, level, passwd)
        e = readPassFileAES(level, passwd)
        print e

def validatePwd(level):
        global saltLength
        
        pw = getpass.getpass('''Enter password: ''')
        h = hashlib.sha512()
        h.update(level)
        dirname = h.hexdigest()
        try:
                f = open(dirname + '/.secret', 'rb')
                test = f.readline()
                pw = enhancePass(test[0:saltLength], pw)
                h.update(pw)
                h.update(test[0:saltLength])
                if test[saltLength:] == h.hexdigest():
                        print '''Password correct'''
                        return pw
                else:
                        raise Exception()
        except:
                print '''Wrong level name or password'''
                sys.exit(0)

def showKey(key):
        s = raw_input("Display key on screen? [y/N] ")
        if s.lower() == 'y':
                print key + '[END]'
        else:
                cb = Tk()
                cb.withdraw()
                cb.clipboard_clear()
                cb.clipboard_append(key)
                raw_input("Password copied.  Press [Enter] after using the password")
                cb.clipboard_clear()

def getNewPass():
        pw1 = getpass.getpass('''Enter a new password: ''')
        pw2 = getpass.getpass('''Repeat your password: ''')
        
        if pw1 != pw2:
                print '''Two password input didn't match, quit'''
                sys.exit(1)
        else:
                return pw1

def createLevel(arg):
        global saltLength
        
        checkArgLength(arg, 1)
        print '''Creating encryption level %s''' % arg
        h = hashlib.sha512()
        h.update(arg[0])
        dirname = h.hexdigest()
        if os.path.isdir(dirname) == True:
                print '''Level already exists.  Ignore request'''
                return
        print '''Creating password for level %s''' % arg[0]
        pw = getNewPass()
        try:
                os.mkdir(dirname, 0700)
                f = open(dirname + '/.secret', 'wb')
                salt = Random.new().read(saltLength)
                f.write(salt)
                pw = enhancePass(salt, pw)
                h.update(pw)
                h.update(salt)
                f.write(h.hexdigest())
                f.close()
                open(dirname + '/.data', 'wb').close()
                os.chmod(dirname + '/.secret', 0600)
                os.chmod(dirname + '/.data', 0600)
                print '''Level %s created successfully''' % arg[0]
        except:
                print '''An error occurred while initializing level'''
                traceback.print_exc()
                if os.path.isdir(dirname) == True:
                        shutil.rmtree(dirname)

def removeLevel(arg):
        checkArgLength(arg, 1)
        print '''Removing encryption level %s''' % arg
        validatePwd(arg[0])
        s = raw_input("Delete level %s? [y/N] " % arg)
        if s.lower() != 'y':
                print '''No action taken'''
                sys.exit(0)
        shutil.rmtree(getDirname(arg[0]))
        print '''Level %s remvoed''' % arg[0]

def backupLevel(level):
        dirname = getDirname(level)
        shutil.copyfile(dirname + '/.secret', dirname + '/.secret_old')
        shutil.copyfile(dirname + '/.data', dirname + '/.data_old')
        shutil.copymode(dirname + '/.secret', dirname + '/.secret_old')
        shutil.copymode(dirname + '/.data', dirname + '/.data_old')

def resetLevel(arg):
        checkArgLength(arg, 1)
        print '''Resetting password of level %s''' % arg
        pw = validatePwd(arg[0])
        backupLevel(arg[0])
        d = readPassFile(arg[0], pw)
        newpw = getNewPass()
        salt = Random.new().read(saltLength)
        newpw = enhancePass(salt, newpw)
        
        h = hashlib.sha512()
        h.update(arg[0])
        h.update(newpw)
        h.update(salt)
        
        f = open(getDirname(arg[0]) + '/.secret', 'wb')
        f.write(salt)
        f.write(h.hexdigest())
        f.close()
        
        writePassFile(d, arg[0], newpw)

def addID(arg):
        checkArgLength(arg, 2)
        print '''Adding ID %s''' % arg
        levelPW = validatePwd(arg[0])
        
        s = raw_input('Generate password randomly? [Y/n] ')
        pw = ''
        if s.lower() == 'y' or s == '':
                pw = genRandomPassHelper()
        else:
                print 'Setting password manually...'
                pw = getNewPass()
        
        d = readPassFile(arg[0], levelPW)
        if d.has_key(arg[1]):
                print '%s already in record.  Quit' % arg[1]
                sys.exit(0)
        d[arg[1]] = pw
        writePassFile(d, arg[0], levelPW)
        showKey(pw)

def deleteID(arg):
        checkArgLength(arg, 2)
        print '''Deleting ID %s''' % arg
        pw = validatePwd(arg[0])
        s = raw_input("Delete entry %s? [y/N] " % arg[1])
        if s.lower() != 'y':
                print '''No action taken'''
                sys.exit(0)
        saved = readPassFile(arg[0], pw)
        if saved.has_key(arg[1]):
                del saved[arg[1]]
                writePassFile(saved, arg[0], pw)
                print '''Done'''
        else:
                print '''%s does not exist''' % arg[1]
                sys.exit(0)

def renameID(arg):
        checkArgLength(arg, 3)
        print '''Renaming ID %s''' % arg
        pw = validatePwd(arg[0])
        saved = readPassFile(arg[0], pw)
        if saved.has_key(arg[1]):
                saved[arg[2]] = saved[arg[1]]
                del saved[arg[1]]
                writePassFile(saved, arg[0], pw)
                print '''Done'''
        else:
                print '''%s does not exist''' % arg[1]
                sys.exit(1)

def queryIDHelper(dic, query):
        print query
        if dic.has_key(query):
                showKey(dic[query])
        else:
                print '''%s does not exist''' % query
                sys.exit(0)

def queryID(arg):
        checkArgLength(arg, 2)
        print '''Querying ID %s''' % arg
        pw = validatePwd(arg[0])
        saved = readPassFile(arg[0], pw)
        queryIDHelper(saved, arg[1])

def displayChoice(dic, lst, idx):
        if idx < len(lst):
                queryIDHelper(dic, lst[idx])
        else:
                print "Wrong index, quit"
                sys.exit(1)

def searchID(arg):
        checkArgLength(arg, 2)
        pw = validatePwd(arg[0])
        saved = readPassFile(arg[0], pw)
        match = list()
        if not saved:
                print "No ids saved in this level yet"
                return
        raw = saved.keys()
        for i in range(len(raw)):
                if raw[i].lower().find(arg[1].lower()) != -1:
                        match.append(raw[i])
        if match:
                match.sort()
                for i in range(len(match)):
                        print "%d)\t%s" % (i, match[i])
                s = raw_input("Hit [Enter] to exit, or enter choice to lookup: ")
                if s:
                        displayChoice(saved, match, int(s))
        else:
                print "No match found"
                       
def listID(arg):
        checkArgLength(arg, 1)
        searchID([arg[0], ''])

def dumpLevel(arg):
        checkArgLength(arg, 1)
        pw = validatePwd(arg[0])
        saved = readPassFile(arg[0], pw)
        if not saved:
                print "Level empty"
                return
        raw = saved.keys()
        cb = Tk()
        cb.withdraw()
        for i in range(len(raw)):
                cb.clipboard_clear()
                cb.clipboard_append(raw[i])
                raw_input("Clipboard: [Key]%s[End], [Enter] to get data" % raw[i])
                cb.clipboard_clear()
                cb.clipboard_append(saved[raw[i]])
                raw_input("Clipboard: [Data]%s[End], [Enter] for next pair" % saved[raw[i]])
        cb.clipboard_clear()

# deprecated
def convertEnc(arg):
        sys.exit("Deprecated function!")
        checkArgLength(arg, 1)
        pw = validatePwd(arg[0])
        blowfishToAES(arg[0], pw)

def main(argv):
        try:
                if argv[0] == "createlevel":
                        createLevel(argv[1:])
                elif argv[0] == "removelevel":
                        removeLevel(argv[1:])
                elif argv[0] == "resetlevel":
                        resetLevel(argv[1:])
                elif argv[0] == "add" or argv[0] == "a":
                        addID(argv[1:])
                elif argv[0] == "delete" or argv[0] == "d":
                        deleteID(argv[1:])
                elif argv[0] == "query" or argv[0] == "q":
                        queryID(argv[1:])
                elif argv[0] == "rename" or argv[0] == "r":
                        renameID(argv[1:])
                elif argv[0] == "list" or argv[0] == "l":
                        listID(argv[1:])
                elif argv[0] == "search" or argv[0] == "s":
                        searchID(argv[1:])
                elif argv[0] == "dump":
                        dumpLevel(argv[1:])
                else:
                        usage()
        except IndexError:
                usage()

if __name__ == "__main__":
        main(sys.argv[1:])
