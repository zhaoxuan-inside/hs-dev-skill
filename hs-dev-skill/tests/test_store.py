"""Boundary and crash-safe write primitives used by execution control."""
from pathlib import Path
import tempfile
import unittest
from hsdev import store


class StoreTests(unittest.TestCase):
    def test_containment_and_symlink_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for relative in ['../outside','/absolute','x/../../escape','x\\escape']:
                with self.assertRaises(ValueError): store.path(root,relative)
            (root/'link').symlink_to(root,target_is_directory=True)
            with self.assertRaises(ValueError): store.path(root,'link/file')
            self.assertEqual(store.path(root,'src/new.py'),root/'src/new.py')

    def test_write_atomically_replaces_without_temp_leaks(self):
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)/'nested/state.json'
            store.write(target,{'revision':1})
            store.write(target,{'revision':2})
            self.assertEqual(store.read(target),{'revision':2})
            self.assertEqual(list(target.parent.glob('.write-*')),[])

    def test_inventory_excludes_control_and_preserves_binary_hashes(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            store.write(root/'src/a.bin',b'\x00\xff')
            store.write(root/'hs-dev/execution/snapshot.bin',b'ignored')
            store.write(root/'.git/config',b'ignored')
            self.assertEqual(store.inventory(root),{'src/a.bin':store.digest(b'\x00\xff')})

    def test_process_lock_conflict_never_steals(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'hs-dev/execution').mkdir(parents=True)
            with store.transaction(root):
                with self.assertRaisesRegex(ValueError,'Another control transaction'):
                    with store.transaction(root): pass
            with store.transaction(root): pass


if __name__=='__main__': unittest.main()
