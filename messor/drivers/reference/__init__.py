import os
from messor.utils import ensure_directory, list_all_files
from messor.settings import FORAGER_BUFFER, FORMICARY_PATH

# This driver uses individual files written to a directory structure that is
# a copy of the source, each containing the checksum of the referenced file as
# their content.
class ChecksumFilesDriver(object):
    @staticmethod
    def _reference_path_from_filename(filename):
        reference = filename.replace(FORMICARY_PATH + '/outbox/', '')
        return os.path.join(FORAGER_BUFFER, 'hosts', reference)

    def ensure_filename_reference(self, filename, checksum):
        reference_path = self._reference_path_from_filename(filename)
        ensure_directory(os.path.dirname(reference_path))
        with open(reference_path, 'w') as f:
            f.write(checksum)

    def _read_checksum_from_file(self, filename):
        with open(filename, 'rb') as f:
            return f.read()

    def _references_path_from_host(self, host):
        return os.path.join(FORAGER_BUFFER, 'hosts', host)

    def _list_all_references_for_host(self, host):
        references_path = self._references_path_from_host(host)
        return list_all_files(references_path)

    def _remove_buffer_path_from_filename(self, filename):
        return filename.replace(os.path.join(FORAGER_BUFFER, 'hosts'), '')

    def file_index_for_host(self, host):
        references = self._list_all_references_for_host(host)
        filenames = map(self._remove_buffer_path_from_filename, references)
        checksums = map(self._read_checksum_from_file, references)
        return zip(filenames, checksums)
