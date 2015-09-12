from messor.drivers.transfer import FlatBufferDriver

def get_transfer_driver():
    return FlatBufferDriver()

def ensure_file_in_buffer(filename, checksum):
    driver = get_transfer_driver()
    driver.ensure_file_in_buffer(filename, checksum)
