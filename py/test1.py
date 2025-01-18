from QRTD import QSR, QRTD_type
from datetime import datetime

#test to set hData to hParts and byck to getData.

def test(input_data):
    sender = QSR()
    
    sender.set_hData(2, input_data)

    test_hData = sender.hData

    sender.hData_to_Parts()

    test_Parts = sender.Parts
    
    sender.Parts_to_hParts()

    test_id = sender.id
    sender.id = 0    
    sender.Parts = []
    sender.hData = b''

    sender.hParts_to_Parts()
    
    output_data = sender.getData()

    assert sender.id == test_id, f"Assert failed: id {sender.id} != {test_id}"
    assert sender.Parts[0] == test_Parts[0], f"Assert failed: Part {sender.Parts[0]} != {test_Parts[0]}"
    assert sender.hData == test_hData, f"Assert failed: hData {sender.hData} != {test_hData}"
    assert input_data == output_data, f"Assert failed: Data {input_data} != {output_data}"




if __name__ == "__main__":
    print("executing :", __file__ ," starting :" ,datetime.now().strftime("%Y-%m-%d %H:%M:%S"))   

    test(b'123456789') 
    test(b'12345689') # pading  = 0
    test(b'1234568') # pading  = 1

    testqsr = QSR()
    test_template = b'123456789'
    test_multibleFraame = test_template * (3*(testqsr._pSize // len(test_template)) + 1)
    test(test_multibleFraame) # more than one part
