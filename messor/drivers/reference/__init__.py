import os
import logging
from rpyc.utils.classic import download, upload

from messor.utils import ensure_directory, list_all_files, calculate_checksum
from messor.settings import FORAGER_BUFFER, FORMICARY_PATH

logger = logging.getLogger(__name__)

# This driver uses individual files written to a directory structure that is
# a copy of the source, each containing the checksum of the referenced file as
# their content.
class ChecksumFilesDriver(object):
    @staticmethod
    def _reference_path_from_filename(filename):
        reference = filename.replace(FORMICARY_PATH + '/outbox/', '')
        return os.path.join(FORAGER_BUFFER, 'hosts', reference)

    def ensure_filename_reference(self, filename, checksum):
	logger.debug("Ensuring filename reference %s for file %s" % \
			(checksum, filename))
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
	logger.debug("Creating file index for host %s" % host)
        references = self._list_all_references_for_host(host)
        filenames = map(self._remove_buffer_path_from_filename, references)
        checksums = map(self._read_checksum_from_file, references)
        return zip(filenames, checksums)

    def purge_file_in_buffer(self, checksum):
        filename = os.path.join(FORAGER_BUFFER, checksum)
        logger.debug("Removing %s from buffer" % checksum)
        os.remove(filename)

    def purge_buffer(self, reference_checksums):
        logger.debug("Purging resolved files from buffer")
        buffer_checksums = list_all_files(FORAGER_BUFFER)
        resolved_checksums = filter(lambda buffer_checksum: buffer_checksum not in reference_checksums, buffer_checksums)
        map(self.purge_file_in_buffer, resolved_checksums)

    def ensure_file_in_buffer(self, filename, checksum, remote_driver):
	logger.debug("Ensuring file in buffer: %s" % filename)
        dst = os.path.join(FORAGER_BUFFER, checksum)

        if not os.path.isfile(dst) or calculate_checksum(dst) != checksum:
	    logger.debug("Copying file to buffer")
            remote_driver.download(filename, dst)
	else:
            logger.debug("File already in buffer, skipping!")

    def ensure_file_in_inbox(self, filename, checksum, remote_driver):
	logger.debug("Ensuring file in inbox: %s" % filename)
        src = os.path.join(FORAGER_BUFFER, checksum)
        dst = FORMICARY_PATH + '/inbox' + filename

        remote_driver.ensure_parent_directory(dst)
        if not remote_driver.isfile(dst) or remote_driver.calculate_checksum(dst) != checksum:
	    logger.debug("Copying file to inbox")
            remote_driver.upload(src, dst)
	else:
	    logger.debug("File already in inbox, skipping!")
