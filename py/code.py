#könnte verbesserung in QRTD bringen?

import struct
import hashlib

class DataEncoder:
    @staticmethod
    def encodeHdata(version, raw_data):
        #raw_data like output of open("binary.bin", "rb")
        
        # Convert raw data to Big-Endian format and Calculate the hash
        data_be = struct.pack('>{}s'.format(len(raw_data)), raw_data)
        hash32byte = hashlib.sha256(data_be).digest()
        
        # Create and encode the frame (Network Byte Order = Big-Endian) 
        hdata = struct.pack('>I32s', version, hash32byte) + data_be
        return hdata, hash32byte

    @staticmethod
    def decodeHdata(hdata):
        # Determine the frame format
        header_size = 36
        frame_format = '>I32s{}s'.format(len(hdata) - header_size)
        
        # Decode the frame (Network Byte Order = Big-Endian)
        version, hash32byte, data = struct.unpack(frame_format, hdata)
        
        # Verify the hash
        raw_data = hdata[header_size:]
        calculated_hash = hashlib.sha256(data).digest()
        if calculated_hash != hash32byte:
             raise ValueError(f"Hash mismatch: data integrity check failed. Calculated hash: {calculated_hash}, Expected hash: {hash32byte} - Version: {version}")
        
        return version, hash32byte, data

    @staticmethod
    def encodePdata(index, amount, idp, data):
        #data is in Big-Endian already
        # Create and encode the frame (Network Byte Order = Big-Endian)
         
        pdata = struct.pack('>III', index, amount, idp) + data
        return pdata

    @staticmethod
    def decodePdata(pdata):
        # Determine the frame format
        frame_format = '>III'
        header_size = struct.calcsize(frame_format)
        
        # Decode the frame (Network Byte Order = Big-Endian)
        index, amount, id = struct.unpack(frame_format, pdata[:header_size])
        data = pdata[header_size:] #data keeps in Big-Endian coding
        return index, amount, id, data


# Example usage
version = 44886
raw_data = b'1234567890'
print(f"Version: {version}")

#with open("git_workflowUSB.zip", "rb") as file:
#    raw_data = file.read()

print("Data len: {}".format(len(raw_data)))if len(raw_data) > 20 else print("Data: ", raw_data)

# Encode Hdata
hdata, hash32byte = DataEncoder.encodeHdata(version, raw_data)
print(f"Hash: {hash32byte.hex()}")

# Decode Hdata
try:
    version, hash32byte, data = DataEncoder.decodeHdata(hdata)
    print(f"#####output")
    print(f"Version: {version}")
    print(f"Hash: {hash32byte.hex()}")
except ValueError as e:
    print(e)

print("Data len: {}".format(len(data)))if len(data) > 20 else print("Data: ", data)

print(f"###################part Data: ")
# Encode Pdata
index = 5
amount = 99965
id = 44886
data = b'1234567890'
pdata = DataEncoder.encodePdata(index, amount, id, data)
print(pdata)

# Decode Pdata
index, amount, id, data = DataEncoder.decodePdata(pdata)
print(f"Index: {index}")
print(f"Amount: {amount}")
print(f"ID: {id}")
print(f"Data: {data}")