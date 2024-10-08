from core.emulator import Emulator
from controller.custom_controller import CustomController
from utils.utility_functions import load_config, build_network_from_config, initialize_controllers, save_results_to_csv
from traffic.flow_manager import FlowManager
from traffic.stats_collector import StatsCollector
from monitoring.monitor import SimulationMonitor
from monitoring.logger import EventLogger
from monitoring.visualizer import NetworkVisualizer

# エミュレータとカスタムコントローラのインスタンスを作成
emulator = Emulator()
controller = CustomController()

# 設定ファイルを読み込む
network_config = load_config('config/network_config.json')
controller_config = load_config('config/controller_config.json')

# ネットワークを設定ファイルに基づいて構築
build_network_from_config(emulator, network_config)

# デバッグ用にエミュレータ内のノードを表示
print("エミュレータ内のノード:")
for name, node in emulator.nodes.items():  # 修正: items() メソッドを使用してキーと値を取り出す
    if isinstance(node, str):
        print(f"エラー: ノードが文字列として格納されています - {name}: {node}")
    else:
        print(f"ノード名: {name}, ノードタイプ: {type(node)}")

# コントローラを設定ファイルに基づいて初期化し、スイッチに追加
initialize_controllers(emulator, controller_config)

# シミュレーションモニタリングを初期化
simulation_monitor = SimulationMonitor(emulator, interval=2)
logger = EventLogger()
visualizer = NetworkVisualizer(network=network_config)

# 統計データを収集する StatsCollector を初期化
stats_collector = StatsCollector(emulator)
stats_collector.start()

# トラフィックフローを管理する FlowManager を初期化
flow_manager = FlowManager()
host1 = emulator.get_node_by_name("Host1")  # 修正: emulator.get_node_by_name を使用してノードを取得
host2_ip = "10.0.0.2"
if host1:
    flow1 = flow_manager.add_flow(host1, host2_ip, interval=1.0, payload="Hello from Host1")

# シミュレーションモニタリングを別スレッドで開始
import threading
monitor_thread = threading.Thread(target=simulation_monitor.start)
monitor_thread.start()

# シミュレーションを実行（5秒間）
emulator.run_simulation(duration=5)

# シミュレーションモニタリングを停止
simulation_monitor.stop()
monitor_thread.join()

# 統計データを表示
stats_collector.print_stats()

# 統計データを CSV ファイルに保存
stats_collector.save_to_csv(folder_path="results", file_prefix="network_stats")

# ネットワークの視覚化を表示
visualizer.visualize_network()

# 統計データの収集を停止
stats_collector.stop()

# ログイベントの記録
logger.log_event("シミュレーションが完了しました。")

# トラフィックフローを削除
flow_manager.clear_all_flows()