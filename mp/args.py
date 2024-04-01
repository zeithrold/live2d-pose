from argparse import ArgumentParser

argparser = ArgumentParser()
argparser.description = "启动WebSocket服务器"
argparser.add_argument(
    "--ip", "-i", default="localhost", type=str, help="server ip to bind"
)
argparser.add_argument(
    "--port", "-p", default=8765, type=int, help="server port to bind"
)
argparser.add_argument(
    "--model", type=str, help="url where stores Live2D model (.model3.json)"
)
argparser.add_argument(
    "--frontend", type=str, help="url where serves KalidoKit frontend"
)
args = argparser.parse_args()
