"""
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE PURPOSE:
    Inital symetric handshake and identity authentication using globably used pre-agreed key (utilised by all clients in p2p network)
    building of an asymetric agreement between hosts for communication such that other clients cannot snoop on private communication between two other endpoints.
    asymetric encoding / decoding of voip and text buffer data prior to and post transmission respectively
    digital signature production and verification to validate source of packets / tampering
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
AUTHOR NOTES:
    Creating a encryption algorithm / solution from scratch is incredibly, INCREDIBLEY difficult to get right, and even a single failure or misunderstanding when implementing an
    aspect of your solution can result in a catastrophy, as a non specialised developer I opted to specifically use pynacl here mostly because I trust the makers of it
    and I also trust the creator of the original nacl library. the solution bellow may seem incredibly simple, but there is a large amount of steps hidden away by PyNacl
    I reccomend reading the cryptography section of my literature review for a brief overview, then a thorough reading of pynacl's doccumentation from top to bottom.

    Because we are not using PKI, web of trust or any other third party utilising authentication method, proof of identity and the security of this method is based on the user password  and five factors:
     - one, the neighbor has the shared, preagreed password and it is sufficently complex to inhibit guessing methods.
     - two, the password isn't compromised and is never shared publicly or stored digitally by the program for future use.
     - three, the client attempts connection to a known good inital client, or client address that they trust minimizing the risk of a bad actor who knows the password or who
              will supply its neighbors with a inital client list that contains bad actors.
     - four, symetric encryption is ONLY used to share enough information to make an asymetric agreement, no voip or text data is symetrically encrypted.
     - five, asymetric encryption provides security for and again'st every other member of the p2p network who knows the password.

     There are a couple of obvious flaws with this approach that must be considered as tradeoff's of this design choice:
     - one, the system is only as strong as the password, which has the potential to be an incredibly weak link, I have tried to strike a balance between randomness, ease of memorization and
            ease of communication prior to using the application. Ultimately, someone could use "tttttttttt" as a password and this model would accept it, thus strong password design is left
             to the user which may not be ideal"
     - two, there is a window of opportunity during symetric encryption usage where an existing member of the p2p network or a third party who knows the password, who also has knowledge of
            an ongoing asymetric negotiation between two hosts could potentially perform a MITM attack, the Symetric encryption authenticator only authenticates that the neighbor is part of
            a niche subset of users who knows the password, not that they are truely a specific or expected member of the p2p network.
    - three, A new asymetric agreement must be made between clients over the Symetric method every time a connection is terminated, Saving asymetric agrements for reuse with known good clients
            in the manner TOFU and SSH do post PAKE would be a significantly better approach, effectively making a password one time use and significantly reducing the amount of chances
            to "crack" the connection.
    - four, Because of the above, as the amount of users on the p2p network grows, the visability of a given password increases and thus its security becomes more and more degraded.
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE TEST CODE:

    #SYMETRIC
    test = Symetric('lorumipsumfarquad') #performed by both clients
    text = b"lorum ipsum"
    text = test.encrypt(text)  # Sender side
    print (text)
    text = test.decrypt(text)  # reciever side
    print (text)

    #ASYMETRIC (This example doesnt account for symetric transfer of npkb and nvkb and is for illustration purposes, look at mukkava socket, or testing/socket_experimentation/5*)
    test2 = Asymetric()  # one side of the exchange
    test3 = Asymetric()  # second side of the exchange
    test2.setup(test3.public_encryption_key, test3.public_verify_key_bytes)
    test3.setup(test2.public_encryption_key, test2.public_verify_key_bytes)
    text = test2.encrypt(b"test")
    print(text)
    text = test3.decrypt(text)
    print(text)
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DISSERTATION NOTES:
    FURTHER DEVELOPMENT: See module notes
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
import nacl.utils
import nacl.secret
from nacl.public import PrivateKey, Box
from nacl.signing import SigningKey, VerifyKey

#Message header constants - Used to add fixed length padding to the header fields so sockets know how much data to recieve Padding_test in first_party_tests shows this well.
message_length_hsize = 4  # constant variable for the message length section of the header in charecter bytes.

class Symetric:  # Symetric encryption (Xsalsa20) and MAC authentication (Poly1305) to encode / decode data. created globally and used initally for all sockets
    def __init__(self, password):
        self.encrypted_hsize = 40 + message_length_hsize  # constant variable for the expected charecter byte size of an individualy symetricaly encrypted header section. Encryption is done individually as we cannot partially decrypt a section of a encrypted message
        self.key = b''
        if len(password) < 12:
            raise ValueError("Supplied password must have a charecter length greater then 10 charecters") # This is an arbitrary length, it would be better to use a perfectly random 32 byte key but this is hard to remember in practice, we want to encourage the user to memorise the password rather then store it where it could potentially be compromised.
        for i in range(0, 32):
            self.key += bytes(password[i % len(password)], encoding='utf8') # Key MUST be 32 Bytes long so we transform the password into a 32byte sequence
        self.symetric_box = nacl.secret.SecretBox(self.key)  # create a box to encrypt and decrypt with

    def encrypt(self, data):  # symetrically encrypt data. expects bytestream input
        if not isinstance(data, bytes):  #There are cases where the data we are using may have allready had to be turned into bytes prior to being encrypted (voice data) in this case we skip encoding so as to avoid double encoding the data.
            data = bytes(data,"utf-8")  # if it isn't, encode it into utf-8 by default
        return self.symetric_box.encrypt(data)

    def decrypt(self, data):  # symetrically decrypt data. expects data to be of type nacl.utils.EncryptedMessage
        data = self.symetric_box.decrypt(data)
        try:  #unfortunately there is no easy way to distinguish flac or key encoded bytes from utf-8
            return data.decode("utf-8").strip()  # Remove encoding from data
        except UnicodeDecodeError:  #We just tried to decode voice data or a encryption key that was never encoded as utf-8, other areas of the program will handle them.
            return data

class Asymetric:  # Asymetric encryption (Curve25519) and  digital signatures (ED25519) to encode / decode data. A new keypair / instance is used per socket session for greater security.
    def __init__(self):
        self.encrypted_hsize = 104 + message_length_hsize  # constant variable for the expected charecter byte size of an individualy asymetrically encrypted header section. Encryption is done individually due to how MACs and DigSigs work.
        self.private_decryption_key = PrivateKey.generate()  # generate Private key pair
        self.public_encryption_key = self.private_decryption_key.public_key  # Fetch the public key
        self.public_encryption_key_bytes = self.public_encryption_key.encode()  #serialised the public key for network transmission during handshake
        self.neighbor_public_key = None  # This will be recieved during the handshake
        self.asymetric_box = None  #this will be created after the handshake

        self.private_signing_key = SigningKey.generate()  # Generate a new pair of keys for digital signing
        self.public_verify_key = self.private_signing_key.verify_key  # ditto of public encryption key, but for verifying message signature
        self.public_verify_key_bytes = self.private_signing_key.verify_key.encode()  # Again, we must serialise this for transmission
        self.neighbor_verify_key = None

    def setup(self, npkb, nvkb):  # this function initalises the Asymetric instance for actual usage once the neighbor has sent their npk and nvk with symetric encryption
        self.neighbor_public_key = nacl.public.PublicKey(npkb)  # Turn npkb back into a public key
        self.neighbor_verify_key = VerifyKey(nvkb)  # turn nvkb back into a public verify key
        self.asymetric_box = Box(self.private_decryption_key, self.neighbor_public_key)  #create our asymetric box using our own private key and the recieved public key

    def encrypt(self, data):  # Asymetrically encrypt data. expects bytestream input
        if not isinstance(data, bytes):
            data = bytes(data, "utf-8")
        return self.asymetric_box.encrypt(self.private_signing_key.sign(data))

    def decrypt(self, data):  # Asymetrically decrypt data. expects data to be of type nacl.utils.EncryptedMessage
        data = self.neighbor_verify_key.verify(self.asymetric_box.decrypt(data))
        try:
            return data.decode("utf-8").strip()
        except UnicodeDecodeError:
            return data

