import os
from QRTD import QSR, QRTD_type
from datetime import datetime

''' data to img and back to data '''


def test(input_data):
    sender = QSR()
    
    sender.set_hData(2, input_data)
    sender.hData_to_Parts()
    sender.Parts_to_hParts()

    receiver = QSR()

    #new in test3
    sender.hParts_to_Imgs()
    sender.save_Imgs_to_directory("./test")

    #send ends here

    receiver.load_Imgs_from_directory("./test")
    
    delete = "y" # clean up test directory
    if delete == "y":
        for file_name in os.listdir("./test"):
            if file_name.endswith(".png"):
                os.remove(os.path.join("./test", file_name))


    receiver.images_to_hParts()

    #end of new in test3
    receiver.hParts_to_Parts()    
    output_data = receiver.getData()

    assert sender.id == receiver.id, f"Assert failed: id {sender.id} != {receiver.id}"
    assert sender.Parts[0] == receiver.Parts[0], f"Assert failed: Part {sender.Parts[0]} != {receiver.Parts[0]}"
    assert sender.hData == receiver.hData, f"Assert failed: hData {sender.hData} != {receiver.hData}"
    assert input_data == output_data, f"Assert failed: Data {input_data} != {output_data}"



def old():
    sender = QSR()
    sender.set_hData(2, input_data)

    print("test      hData:", sender.hData)  
    #print("test Data:", handler.getData())

    sender.hData_to_Parts()
    #print("done: HData_to_Parts()")
    test_hData = sender.hData


    sender.Parts_to_hParts()
    #print("done: Parts_to_HParts()")
    
    sender.hParts_to_Imgs()
    #print("done: HParts_to_QRImgs()")

    sender.save_Imgs_to_directory("./test")
    #print("done: save_images_to_directory()")
    
    receiver = QSR()
    receiver.load_Imgs_from_directory("./test")
    #print("done: load_images_from_directory()")
    
    delete = "y"
    if delete == "y":
        for file_name in os.listdir("./test"):
            if file_name.endswith(".png"):
                os.remove(os.path.join("./test", file_name))

    
    
    print("done: receiver img len: ", len(receiver.images))

    receiver.images_to_hParts()
    print("done: images_to_hparts()")

    print("\nAssert: hPart :\n", sender.hParts[0], "\n", receiver.hParts[0])   


    

    progress = receiver.gethProgress()
    print("done progress: ", progress)


    receiver.hParts_to_Parts()
    print("done: HParts_to_Parts()")
    
    print("\nAssert: Part :\n", sender.Parts[0], "\n", receiver.Parts[0])   

    progress = receiver.getProgress()
    print("done progress: ", progress)

    out = receiver.getData()
    print("\nAssert: Data :\n", input_data, "\n", out)       

    


    

if __name__ == "__main__":
    print("executing :", __file__ ," starting :" ,datetime.now().strftime("%Y-%m-%d %H:%M:%S"))   
    test_data = b'123456789'
    test(test_data) 
    print("done: ",test_data)
    
    test_data = b'12345689' # pading  = 0
    test(test_data) 
    print("done: ",test_data)
    
    test_data = b'1234568' # pading  = 1
    test(test_data) 
    print("done: ",test_data)
    
    testqsr = QSR()
    test_data = b'123456789'
    test_multibleFraame = test_data * (3*(testqsr._pSize // len(test_data)) + 1)
    test(test_multibleFraame) # more than one part
    print("done: ",test_data)
    
