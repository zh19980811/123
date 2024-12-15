# 城市收入增长计算网页脚本（最终税率单独放一栏）
# 将代码修改为可在网页上运行的 Flask 应用，允许设定起始税率和最终税率

from flask import Flask, request, render_template_string, session
from flask_session import Session

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# HTML 模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>城市收入增长计算器</title>
</head>
<body>
    <h1>城市收入增长计算器</h1>
    <form method="post">
        <h2>初始参数</h2>
        <label>初始农业: <input type="number" name="agri" value="{{ agri }}"></label><br>
        <label>初始商业: <input type="number" name="comm" value="{{ comm }}"></label><br>
        <label>初始矿业: <input type="number" name="mine" value="{{ mine }}"></label><br>
        <label>初始海港: <input type="number" name="port" value="{{ port }}"></label><br>
        <label>初始人口: <input type="number" name="pop" value="{{ pop }}"></label><br>
        <label>初始壮丁: <input type="number" name="soldiers" value="{{ soldiers }}"></label><br>
        <label>初始税率 (%): <input type="number" step="0.01" name="tax_start" value="{{ tax_start }}"></label><br><br>

        <h2>最终税率设置</h2>
        <label>最终税率 (%): <input type="number" step="0.01" name="tax_end" value="{{ tax_end }}"></label><br><br>

        <h2>地图城市分布</h2>
        <label>总城市数量: <input type="number" name="total_cities" value="{{ total_cities }}"></label><br>
        <label>农业城市数量: <input type="number" name="agri_cities" value="{{ agri_cities }}"></label><br>
        <label>商业城市数量: <input type="number" name="comm_cities" value="{{ comm_cities }}"></label><br>
        <label>矿业城市数量: <input type="number" name="mine_cities" value="{{ mine_cities }}"></label><br>
        <label>海港城市数量: <input type="number" name="port_cities" value="{{ port_cities }}"></label><br><br>

        <h2>每回合增长参数</h2>
        <label>每回合农业增长: <input type="number" name="agri_growth" value="{{ agri_growth }}"></label><br>
        <label>每回合商业增长: <input type="number" name="comm_growth" value="{{ comm_growth }}"></label><br>
        <label>每回合矿业增长: <input type="number" name="mine_growth" value="{{ mine_growth }}"></label><br>
        <label>每回合人口增长: <input type="number" name="pop_growth" value="{{ pop_growth }}"></label><br>
        <label>每回合壮丁增长: <input type="number" name="soldiers_growth" value="{{ soldiers_growth }}"></label><br>
        <label>回合数: <input type="number" name="rounds" value="{{ rounds }}"></label><br><br>

        <input type="submit" value="计算收入增长">
    </form>

    {% if result is not none %}
        <h2>结果: 城市总收入增长比例为 {{ result }}%</h2>
    {% endif %}
</body>
</html>
"""

def calculate_growth(cities, growth, rounds, tax_start, tax_end):
    """
    计算城市收入增长，税率线性变化
    :param cities: 初始城市参数 (农业, 商业, 矿业, 海港, 人口, 壮丁)
    :param growth: 每回合增长参数 (农业, 商业, 矿业, 人口, 壮丁)
    :param rounds: 总回合数
    :param tax_start: 初始税率
    :param tax_end: 最终税率
    :return: 最终收入增长比例
    """
    # 初始参数
    agri, comm, mine, port, pop, soldiers = cities
    agri_growth, comm_growth, mine_growth, pop_growth, soldiers_growth = growth
    tax = tax_start
    tax_step = (tax_end - tax_start) / rounds  # 每回合税率变化量

    # 各类型城市权重
    city_weights = {
        '农业': 5,  # 农业型城市
        '商业': 2,  # 商业型城市
        '矿业': 4,  # 矿业型城市
        '海港': 3,  # 海港型城市
    }

    # 初始收入公式
    initial_revenue = (
        (city_weights['农业'] * agri + city_weights['商业'] * comm + city_weights['矿业'] * mine + city_weights['海港'] * port)
        * (pop + soldiers) * tax / 100
    )

    # 每回合增长叠加计算（税率线性变化）
    for _ in range(rounds):
        agri += agri_growth
        comm += comm_growth
        mine += mine_growth
        pop += pop_growth
        soldiers += soldiers_growth
        tax += tax_step

    # 最终收入公式
    final_revenue = (
        (city_weights['农业'] * agri + city_weights['商业'] * comm + city_weights['矿业'] * mine + city_weights['海港'] * port)
        * (pop + soldiers) * tax / 100
    )

    # 收入增长比例
    growth_percentage = (final_revenue - initial_revenue) / initial_revenue * 100
    return round(growth_percentage, 2)

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'state' not in session:
        # 初始化状态
        session['state'] = {
            'agri': 66, 'comm': 33, 'mine': 30, 'port': 15,
            'pop': 4880000, 'soldiers': 920000, 'tax_start': 15, 'tax_end': 17,
            'agri_growth': 2, 'comm_growth': 2, 'mine_growth': 0,
            'pop_growth': 10000, 'soldiers_growth': 10000, 'rounds': 12,
            'total_cities': 10, 'agri_cities': 6, 'comm_cities': 2, 'mine_cities': 1, 'port_cities': 1
        }

    state = session['state']
    result = None
    if request.method == 'POST':
        # 获取表单数据
        agri = float(request.form['agri'])
        comm = float(request.form['comm'])
        mine = float(request.form['mine'])
        port = float(request.form['port'])
        pop = float(request.form['pop'])
        soldiers = float(request.form['soldiers'])
        tax_start = float(request.form['tax_start'])
        tax_end = float(request.form['tax_end'])

        agri_growth = float(request.form['agri_growth'])
        comm_growth = float(request.form['comm_growth'])
        mine_growth = float(request.form['mine_growth'])
        pop_growth = float(request.form['pop_growth'])
        soldiers_growth = float(request.form['soldiers_growth'])
        rounds = int(request.form['rounds'])

        # 计算增长率
        result = calculate_growth(
            (agri, comm, mine, port, pop, soldiers),
            (agri_growth, comm_growth, mine_growth, pop_growth, soldiers_growth),
            rounds, tax_start, tax_end
        )

        # 保存状态
        state.update({
            'agri': agri, 'comm': comm, 'mine': mine, 'port': port,
            'pop': pop, 'soldiers': soldiers, 'tax_start': tax_start, 'tax_end': tax_end,
            'agri_growth': agri_growth, 'comm_growth': comm_growth,
            'mine_growth': mine_growth, 'pop_growth': pop_growth,
            'soldiers_growth': soldiers_growth, 'rounds': rounds
        })
        session['state'] = state

    return render_template_string(HTML_TEMPLATE, result=result, **state)

if __name__ == '__main__':
    app.run(debug=True)