import sys
sys.path.insert(0, '/app')
from engines.video_manager import VideoManager

vm = VideoManager()
print(f"Pexels key set:  {bool(vm.pexels_key)}")
print(f"Pixabay key set: {bool(vm.pixabay_key)}")

for topic in ["technology", "nature landscape", "city night"]:
    v = vm.get_video(topic)
    if v:
        print(f"\n{topic}:")
        print(f"  source:   {v['source']}")
        print(f"  duration: {v['duration']}s")
        print(f"  url:      {v['url'][:90]}")
    else:
        print(f"\n{topic}: NONE")