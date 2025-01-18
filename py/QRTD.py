import hashlib
import sys
import qrcode
from PIL import Image
from pyzbar.pyzbar import decode
import os
import zipfile
import struct
import base64


def max_frame_length(max_qr_length): #the qr code is 4/3 the size of the frame data - we need to set the frame size sall enough to fit into the qr code. 
    return (max_qr_length // 4) * 3
# Define maximum capacities for error correction levels (in bytes)
MAX_CAPACITIES = {
    "Low": 2953, #not tested
    "Medium": 2331, #not tested
    "Quartile": 1663, #tested
    "High": 1273 #not tested
}


def byteA2NetworkByteArray(data):
    # Bestimme die Anzahl der Integer im Bytearray

    if len(data) % 4 != 0:
        raise ValueError("Data length must be divisible by 4.")

    num_integers = len(data) // 4
    
    # Bestimme die Endianness des Systems
    system_endianness = '<' if sys.byteorder == 'little' else '>'
    
    # Konvertiere das Bytearray in eine Liste von Integern basierend auf der System-Endianness
    integers = struct.unpack(f'{system_endianness}{num_integers}i', data)
    
    # Konvertiere die Liste von Integern in ein big-endian Bytearray
    big_endian_bytes = b''.join(struct.pack('>i', i) for i in integers)
    
    return big_endian_bytes

def NetworkByteArray2byteA(data):
    # Bestimme die Anzahl der Integer im Bytearray

    if len(data) % 4 != 0:
        raise ValueError(f"Data length must be divisible by 4. is {len(data)} -%-> {len(data) % 4}")

    num_integers = len(data) // 4
    
    # Konvertiere das Bytearray in eine Liste von Integern im big-endian Format
    integers = struct.unpack(f'>{num_integers}i', data)
    
    # Bestimme die Endianness des Systems
    system_endianness = '<' if sys.byteorder == 'little' else '>'
    
    # Konvertiere die Liste von Integern in ein Bytearray basierend auf der System-Endianness
    system_endian_bytes = b''.join(struct.pack(f'{system_endianness}i', i) for i in integers)
    
    return system_endian_bytes



class QRTD_type:
    INIT = 0
    ISO_TEXT = 1
    ZIP_BINARY = 2


class QSR:
    NC = 'big'  # Network coding big endian

    def __init__(self):
        self.hData = []

        self.Parts = []
        

        self.hParts =[]
        
        self.data = []
        self.type = QRTD_type.INIT  # Version or Datatype information internally set
        self.hash = bytearray(32)  # hash to all the data

        self.id = 0
        self._pSize = max_frame_length(MAX_CAPACITIES["Quartile"])  # size to slice the data into chunks to fit into QR code standards
        self.images = []


    def set_hData(self, type, data): #entry for encoding
        if self.type == QRTD_type.INIT and type != QRTD_type.INIT:
            self.type = type
        else:
            raise ValueError("Unsupported type")
        
        # Generate hash - no padding
        hash_object = hashlib.sha256(data)
        self.hash = hash_object.digest()  # 32 bytes
        #print("setHData    HASH: ", self.hash, " len ", len(self.hash))

        endianness = 'little' if sys.byteorder == 'little' else 'big'
        self.id = int.from_bytes(self.hash[0:4], endianness)
        #print("setHData      ID: ", self.id)

        # Ensure the length of data is a multiple of 4
        padding_length = (4 - len(data) % 4) % 4
        #print("setHData len pad: ", padding_length)  
        padded_data = data + b'\x00' * padding_length

        # Format of hdata: 4 byte type - 4 byte padding length - 32 byte sha256 - n byte data + padding
        self.hData = self.type.to_bytes(4, self.NC) + padding_length.to_bytes(4, self.NC) + byteA2NetworkByteArray(self.hash) + byteA2NetworkByteArray(padded_data)
        #print("setHData hdata: ", self.hData)   

    def getData(self): #entry for decoding after receive finished.
        # Format of hdata: 4 byte type - 4 byte padding length - 32 byte sha256 - n byte data + padding
        
        if self.getProgress()  != 0:
            return None
        
        self.hData  = b''.join(self.Parts)

        type = int.from_bytes(self.hData[0:4], self.NC)
        #print("getData   type: ", type)

        padding_length = int.from_bytes(self.hData[4:8], self.NC)
        #print("getData len pad: ", padding_length)
        
        hash = NetworkByteArray2byteA(self.hData[8:40])
        #print("getData   HASH: ", hash, " len ", len(hash))
        
        data = NetworkByteArray2byteA(self.hData[40:])
        
        if padding_length > 0:
            return data[:-padding_length]
        else:
            return data
        
    def hData_to_Parts(self):
         # Slice hdata into n parts with size _pSize
        self.Parts = [self.hData[i:i+self._pSize] for i in range(0, len(self.hData), self._pSize)]
        #print("HData_to_Parts: ", len(self.Parts), " parts")    

    
    def Part_to_hPart(self, index):
        # Format of parts: 4 byte part index - 4 byte number of parts - 4 byte hash as ID - _pSize byte of data
        self.hParts[index] = index.to_bytes(4, self.NC) + len(self.Parts).to_bytes(4, self.NC) + self.id.to_bytes(4,self.NC) + self.Parts[index]
        

    def hPart_to_Part(self, inHPart):
        if inHPart is None:
            #print("HPart_to_Part: inHPart is None")
            return None
        
        
        index, nParts, id, data = self.decode_hPart(inHPart)

        #index = int.from_bytes(inHPart[0:4], self.NC)
        #nParts = int.from_bytes(inHPart[4:8], self.NC)
        #print("HPart_to_Part: ", index, " of ", nParts)
        
        #id = inHPart[8:12]
        #print("HPart_to_Part: ID: ", id)

        if self.id == 0:
            self.id = id


        if id != self.id:
            print("HPart_to_Part: ID not matching")
            return None

        #data = inHPart[12:]
        return data

    def Parts_to_hParts(self):
        if len(self.hParts) is not len(self.Parts):
            if len(self.hParts) != 0:
                print("Parts_to_HParts: hparts len Parts not equal")
            self.hParts =  [[] for _ in range(len(self.Parts))]
        for i in range(len(self.Parts)):
            self.Part_to_hPart(i)  

    def hParts_to_Parts(self):
        if len(self.hParts) != len(self.Parts):
            if len(self.Parts) != 0:
                print("HParts_to_Parts: hParts len and Parts len not equal")
            self.Parts = [[] for _ in range(len(self.hParts))]
        for i in range(len(self.hParts)):
            #print(f"HParts_to_Parts: Processing part {i}")
            data = self.hPart_to_Part(self.hParts[i])
            if data is not None:
                self.Parts[i] = data
    
    def hParts_to_Imgs(self):
        if len(self.images) != 0: 
            return -1  # error do not set images twice
        for i in range(len(self.hParts)):
            img = self.hPart_to_Img(self.hParts[i])
            self.images.append(img)

    def hPart_to_Img(self,data):
        encoded_data = base64.b64encode(data)
        #print("hPart_to_Img: len data:  ---->>>>   ", len(data))  
        #print("hPart_to_Img: len enco:  ---->>>>   ", len(encoded_data))  
        qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=1,
                border=1,
            )
        qr.add_data(encoded_data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        return img
    
    def save_Imgs_to_directory(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        for i, img in enumerate(self.images): # save all images with the id in the name
            img_path = os.path.join(directory, f"qr_{self.id}_{i}.png") # hex() because of allowed characters in file names
            img.save(img_path)
    
    def clear_Imgs(self):
        self.images = []

    def load_Imgs_from_directory(self, directory, reset = False): #will clear the old images before loading if reset is set to True
        if reset:
            self.clear_Imgs()
        
        for file_name in os.listdir(directory):
            if file_name.endswith(".png"):
                img_path = os.path.join(directory, file_name)
                with Image.open(img_path) as img:
                    self.images.append(img.convert('RGB'))
                #print("IMG: ", file_name)

    def Img_to_hPart(self, img, process_all = False): #to do implement true path
        """
            This function takes an image (img) and searches for QR codes within it.
            It checks if the QR codes belong to the current class and adds the hPart data and retruns self.
            If no matching code is found the function returns None.
            Optionally, the function can be extended to generate new QSR objects and return a list 
            of QSR objects if QR codes from other data are found in the image.

            Parameters:
            img (Image): The image to be searched for QR codes.
            generate_new_qsr (bool, optional): If True, new QSR objects are generated and returned if QR codes
                                            from other data are found in the image. Default is False.
        """
        #print("Image type:", type(img))
        #print("Image mode:", img.mode)
        
        if img.mode not in ['RGB', 'L']:
            img = img.convert('RGB')
            #print("Converted image mode:", img.mode)
        
        try:
            qrs = decode(img)
            #print("img_to_hPart #qr ", len(qrs))
        except Exception as e:
            print("img_to_hPart Error decoding image:", e)
            return None
        
        if len(qrs) != 1:
            print("img_to_hPart Codes in picture - " + str(len(qrs)))
        
        for qr in qrs:
            qr_data = base64.b64decode(qr.data)
            #print("img_to_hPart qr Data - len ----- " + str(len(qr.data)))
            #print("img_to_hPart qr Data - len ----- " + str(len(qr_data)))
            if len(qr.data) < 13:  # a coded part has at least the header plus one byte of data
                print("img_to_hPart Codes size < header size - " + str(len(qr.data)))
                continue 

            index, nParts, idQR, data = self.decode_hPart(qr_data)
            #print("img_to_hPart index, nParts, idQR, data: ", index, nParts, idQR, "\n", data) 

            
            if index >= nParts: #no valid hPart
                print("img_to_hPart index >= nParts - " + str(index) + " >= " + str(nParts))
                continue
            
            #todo implement crc

            if len(self.hParts) == 0: # create parts
                self.hParts = [[] for _ in range(nParts)]
                #print("img_to_hPart first hPart" )
            
            elif len(self.hParts) != nParts:
                print("img_to_hPart Part number mismatch " + str(len(self.Parts)) + " <- " + str(nParts))
            
            if self.id == 0:
                self.id = idQR
                #print("img_to_hPart ID set to ", self.id)
                
            elif self.id != idQR: 
                print("img_to_hPart ID mismatch " + self.id + " <- " + idQR)    
            
            #print("img_to_hPart index, len(self.Parts): ",index," ", len(self.hParts))
            if self.hParts[index] == []:
                self.hParts[index] = qr_data
                #print("img_to_hPart hPart added " + str(index))


    def images_to_hParts(self):
        for img in self.images:
            #print("images_to_hparts: Processing image")
            self.Img_to_hPart(img)

    def gethProgress(self): #returns files left to finish the job
        if len(self.hParts) == 0:
            return -1
        
        missing_parts = sum(1 for hPart in self.hParts if hPart == [])
        return missing_parts

    def getProgress(self): #returns files left to finish the job
        if len(self.Parts) == 0:
            return -1
        
        missing_parts = sum(1 for part in self.Parts if part == [])
        return missing_parts

    def decode_hPart(self,hPart):#no valid hPart
        # Format of HParts: 4 byte part index - 4 byte number of parts - 4 byte hash as ID - _pSize byte of data
        
        if len(hPart) <= 12:
            return 0, 0, 0, [] 

        index = int.from_bytes(hPart[0:4], self.NC)
        nParts = int.from_bytes(hPart[4:8], self.NC)
        idQR = int.from_bytes(hPart[8:12], self.NC)
        data = hPart[12:]

        if index >= nParts: #no valid hPart
            return 0, 0, 0, []

        return index, nParts, idQR, data

            

