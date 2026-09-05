from pathlib import Path
import model
original=model.MODEL
backup=Path(str(original)+'.recovery-backup')
if original.exists(): original.replace(backup)
try:
    bundle=model.load_model()
    assert 'pipeline' in bundle and hasattr(bundle['pipeline'],'predict')
    print('PASS: model trains and saves when cached artifact is unavailable')
finally:
    if original.exists(): original.unlink()
    if backup.exists(): backup.replace(original)
