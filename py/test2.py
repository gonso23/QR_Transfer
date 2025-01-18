import os
from QRTD import QSR, QRTD_type
from datetime import datetime

# same as test1 but with sender receiver object
# test to set hData to hParts and byck to getData.



def test(input_data):
    sender = QSR()
    
    sender.set_hData(2, input_data)

    sender.hData_to_Parts()

    sender.Parts
    
    sender.Parts_to_hParts()


    receiver = QSR()
    receiver.hParts = sender.hParts

    receiver.hParts_to_Parts()    
    output_data = receiver.getData()

    assert sender.id == receiver.id, f"Assert failed: id {sender.id} != {receiver.id}"
    assert sender.Parts[0] == receiver.Parts[0], f"Assert failed: Part {sender.Parts[0]} != {receiver.Parts[0]}"
    assert sender.hData == receiver.hData, f"Assert failed: hData {sender.hData} != {receiver.hData}"
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
