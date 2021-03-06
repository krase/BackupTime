# -*- coding: utf-8 -*-

import os, sys, time
import logging
from disks import *
from operations import Operations

logger = logging.getLogger("backup")
console = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(console)
logger.setLevel(logging.DEBUG)
console.setLevel(logging.DEBUG)
console.setFormatter(logging.Formatter('%(name)s: %(message)s'))

__all__ = ['Backup']

def progress(complete, partial):
	print "   %d\x0D"%((float(partial)/complete)*100),


class BackupException(Exception):
	pass

class PrepareException(BackupException):
	#error in rsync_dryrun stage
	message = "Failed to prepare backup" 

class SyncException(BackupException):
	#error in rsync stage
	message = "Failed to execute backup" 

class FinalizeException(BackupException):
	message = "Failed to finalize backup"

class Backup(object):
	def __init__(self, backup_disk, source_dir = None, backup_sub_dir = ''):
		assert(isinstance(backup_disk, DiskInfo))
		
		if not backup_disk.is_mounted():
			raise Exception("Drive %s is not mounted"%backup_disk.dev_file())
		if not backup_disk.mount_path():
			raise Exception("Could not determine mount path of backup drive %s"%backup_disk.dev_file())
		
		self.backup_disk = backup_disk
		self.source_dir = source_dir
		self.backup_base_dir = os.path.join(backup_disk.mount_path(), backup_sub_dir)
		self.latest_dir = os.path.join(self.backup_base_dir, 'latest')
		self.op = Operations()

	def can_backup(self, dinfo):
		#has_backup_drive

		#backup_base_dir_ok
		
		#subvol_ok

		#volume_mounted
		return True

	def prepare_backup(self):
		pass

	def do_backup(self):
		logger.info("* dryrun")
		lines = 0
		ok, ret = self.op.sync_dryrun(self.source_dir, self.latest_dir)
		if ok:
			lines = ret
		else:
			raise PrepareException()
		
		logger.info("* sync")
		ret = self.op.sync_data(self.source_dir, self.latest_dir, lambda x: progress(lines, x))
		if not ret:
			raise SyncException()

		logger.info("* snapshot")
		destname = "backup_%d"%int(time.time())
		dest_dir = os.path.join(self.backup_base_dir, destname)
		ret = self.op.create_snapshot(self.latest_dir, dest_dir)
		if not ret:
			raise FinalizeException()

	def delete_backup(self, unix_time):
		voldir = "backup_%d"%int(unix_time)
		logger.info("* deleting snapshot %s", voldir)
		voldir = os.path.join(self.backup_base_dir, voldir)
		ret = self.op.delete_snapshot(voldir)

# vim:ts=3:sts=3:sw=3:noexpandtab
