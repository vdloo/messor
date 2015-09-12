from messor.drivers.reference import ChecksumFilesDriver

def get_reference_driver():
    return ChecksumFilesDriver()

def ensure_filename_reference(filename, checksum):
    driver = get_reference_driver()
    driver.ensure_filename_reference(filename, checksum)
