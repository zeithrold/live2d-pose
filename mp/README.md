## Mediapipe on Jetbot Installation Instruction

Reference on [This CSDN Post](https://blog.csdn.net/weixin_52167116/article/details/121482609)

[TOC]

### Clone Repository
Clone the Mediapipe first
```bash
git clone https://github.com/google/mediapipe.git
cd mediapipe
git checkout 0.8.11
```

### Dependencies

Install building dependencies
```bash
sudo apt-get update
sudo apt-get install -y pkg-config zip gcc-8 g++-8 zlib1g-dev unzip python3-dev cmake
cd /usr/bin
sudo rm gcc g++
sudo ln -s gcc-8 gcc
sudo ln -s g++-8 g++
```


Then, install Bazel 4.0
```bash
sudo apt install apt-transport-https curl gnupg -y
curl -fsSL https://bazel.build/bazel-release.pub.gpg | gpg --dearmor >bazel-archive-keyring.gpg
sudo mv bazel-archive-keyring.gpg /usr/share/keyrings
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/bazel-archive-keyring.gpg] https://storage.googleapis.com/bazel-apt stable jdk1.8" | sudo tee /etc/apt/sources.list.d/bazel.list
sudo apt update && sudo apt-get install -y bazel-4.0.0
```

Download protobuf and install
```bash
wget https://github.com/protocolbuffers/protobuf/releases/download/v3.20.3/protoc-3.20.3-linux-aarch_64.zip
unzip protoc-3.20.3-linux-aarch_64.zip
cd protoc-3.20.3-linux-aarch_64
sudo cp bin/protoc /usr/local/bin/
sudo cp -r include/* /usr/local/include/
cd ..
```

### Patching

Patch the `third_party/BUILD` file

```diff
diff --git a/third_party/BUILD b/third_party/BUILD
index e2044cfd..e8ace04d 100644
--- a/third_party/BUILD
+++ b/third_party/BUILD
@@ -113,6 +113,8 @@ cmake_external(
         "WITH_PNG": "ON",
         "WITH_TIFF": "ON",
         "WITH_WEBP": "OFF",
+        "ENABLE_NEON": "OFF",
+        "WITH_TENGINE": "OFF",
         # Optimization flags
         "CV_ENABLE_INTRINSICS": "ON",
         "WITH_EIGEN": "ON",
```

> The following patch modifies setup.py to specify build lib directory. However, **MediaPipe v0.8.11** supports auto-location to Python build lib. Therefore don't patch it first unless build fail.
> ```patch
> diff --git a/setup.py b/setup.py
> index 8a4c7127..75f9b880 100644
> --- a/setup.py
> +++ b/setup.py
> @@ -209,7 +209,7 @@ class GeneratePyProtos(setuptools.Command):
>          sys.stderr.write('cannot find required file: %s\n' % source)
>          sys.exit(-1)
>  
> -      protoc_command = [self._protoc, '-I.', > '--python_out=.', source]
> +      protoc_command = [self._protoc, '-I.', > '-I/usr/local/include', '--python_out=.', source] # Skeptical if unnecessary on MediaPipe v0.8.11
>        if subprocess.call(protoc_command) != 0:
>          sys.exit(-1)
> ```

```bash
cd mediapipe
git apply check build.patch
```

Remove Unnecessary modules
```bash
cd mediapipe
sed -i -e "/\"imgcodecs\"/d;/\"calib3d\"/d;/\"features2d\"/d;/\"highgui\"/d;/\"video\"/d;/\"videoio\"/d" third_party/BUILD
sed -i -e "/-ljpeg/d;/-lpng/d;/-ltiff/d;/-lImath/d;/-lIlmImf/d;/-lHalf/d;/-lIex/d;/-lIlmThread/d;/-lrt/d;/-ldc1394/d;/-lavcodec/d;/-lavformat/d;/-lavutil/d;/-lswscale/d;/-lavresample/d" third_party/BUILD
```

```bash
python3 setup.py gen_protos && python3 setup.py bdist_wheel
```
