"""测试加载全部 4 个检测器及其权重"""
from inference import load_default_model
import weight_config as config

success = []
failed = []
for det, path in config.discover_weights():
    print(f"[Test] Loading {det} from {path} ...")
    try:
        m = load_default_model(detector_name=det, weights_path=path)
        print(f"  -> OK")
        success.append(det)
    except Exception as e:
        print(f"  -> FAILED: {e}")
        failed.append((det, str(e)))

print("\n========== Summary ==========")
print(f"Success: {success}")
print(f"Failed:  {failed}")
