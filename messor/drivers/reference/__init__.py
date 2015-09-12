import os
from messor.utils import ensure_directory
from messor.settings import FORAGER_BUFFER, FORMICARY_PATH

# This driver uses individual files written to a directory structure that is
# a copy of the source, each containing the checksum of the referenced file as
# their content.
class ChecksumFilesDriver(object):
    @staticmethod
    def _reference_path_from_filename(filename):
        reference = filename.replace(FORMICARY_PATH + '/outbox/', '')
        return os.path.join(FORAGER_BUFFER, "hosts", reference)

    def ensure_filename_reference(self, filename, checksum):
        reference_path = self._reference_path_from_filename(filename)
        ensure_directory(os.path.dirname(reference_path))
        with open(reference_path, 'w') as f:
            f.write(checksum)
