"""
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE PURPOSE:
    Inital symetric handshake and identity authentication using globably used pre-agreed key (utilised by all clients in p2p network)
    building of an asymetric agreement between hosts for communication such that other clients cannot snoop on private communication between two other endpoints.
    asymetric encoding / decoding of voip and text buffer data prior to and post transmission respectively
    digital signature production and verification to validate source of packets / tampering
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE NOTES:
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
    TODO: implement Saving of asymetric keys??
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
MODULE TEST CODE:

    #SYMETRIC
    test = Symetric(lorumipsumfarquad) #performed by both clients
    text = b"lorum ipsum"
    text = test.encrypt(text)  # Sender side
    print (text)
    text = test.decrypt(text)  # reciever side
    print (text)

    #ASYMETRIC (This example doesnt account for symetric transfer of npk and nvkb and is for illustration purposes)
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
    FURTHER DEVELOPMENT: See flaws section of Module
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
import nacl.utils
import nacl.secret
from nacl.public import PrivateKey, Box
from nacl.signing import SigningKey, VerifyKey


class Symetric:  # Symetric encryption (Xsalsa20) and MAC authentication (Poly1305) to encode / decode data. created globally and used initally for all sockets
    def __init__(self, password):
        self.key = b''
        if len(password) < 12:
            raise ValueError("Supplied password must have a charecter length greater then 10 charecters") # This is an arbitrary length, it would be better to use a perfectly random 32 byte key but this is hard to remember in practice
        for i in range(0, 32):
            self.key += bytes(i + password[i % len(password)], encoding='utf8') # Key MUST be 32 Bytes long so we transform the password into a 32byte sequence
        self.symetric_box = nacl.secret.SecretBox(self.key)  # create a box to encrypt and decrypt with


    def encrypt(self, data):  # symetrically encrypt data
        return self.symetric_box.encrypt(data)

    def decrypt(self, data):  # symetrically decrypt data
        return self.symetric_box.decrypt(data)


class Asymetric:  # Asymetric encryption (Curve25519) and  digital signatures (ED25519) to encode / decode data. created individually per socket session
    def __init__(self):
        self.private_decryption_key = PrivateKey.generate()
        self.public_encryption_key = self.private_decryption_key.public_key
        self.neighbor_public_key = None
        self.asymetric_box = None

        self.private_signing_key = SigningKey.generate()
        self.public_verify_key = self.private_signing_key.verify_key
        self.public_verify_key_bytes = self.public_verify_key.encode()
        self.neighbor_verify_key = None

    def setup(self, npk, nvkb):  # this function initalises the Asymetric instance for actual usage once the neighbor has sent their npk and nvk with symetric encryption
        self.neighbor_public_key = npk
        self.neighbor_verify_key = VerifyKey(nvkb)
        self.asymetric_box = Box(self.private_decryption_key, self.neighbor_public_key)

    def encrypt(self, data):
        return self.asymetric_box.encrypt(self.private_signing_key.sign(data))

    def decrypt(self, data):
        return self.neighbor_verify_key.verify(self.asymetric_box.decrypt(data))
