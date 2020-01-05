
import os
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Bar, Grid, Line, Scatter, Geo, Map, Timeline, Page
from flask import Flask, render_template, request
from loguru import logger
from pprint import pprint
rootPath = os.getcwd()

# 导入2010-2016年分省互联网普及率（%）
dfi = pd.read_csv(rootPath + "/internet.csv", dtype='object')

# 导入2013-2018年分省电商销售额（亿元）
dfs = pd.read_csv(rootPath + "/E_sales.csv")

# 导入2014-2018年分省GDP（亿元）
dfg = pd.read_csv(rootPath + "/GDP.csv")

# 导入2012-2019中国最具幸福感城市前10排行榜
dfh = pd.read_csv(rootPath + "/happiness_times.csv")

def grid_mutil_yaxis(data, info):
    x_data = data[0]
    bar = (
        Bar()
            .add_xaxis(x_data)
            .add_yaxis(info[0],
                       data[1],
                       yaxis_index=0,
                       color="#5793f3",
                       )
            .extend_axis(
            yaxis=opts.AxisOpts(
                name="“最具幸福感城市”上榜次数",
                type_="value",
                min_=0,
                max_=20,
                position="right",
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(color="#d14a61")
                ),
                axislabel_opts=opts.LabelOpts(formatter="{value}"),
                splitline_opts=opts.SplitLineOpts(
                    is_show=True, linestyle_opts=opts.LineStyleOpts(opacity=1)
                ),
            )
        )
            .set_global_opts(
            xaxis_opts=opts.AxisOpts(type_="category",
                                     axislabel_opts=opts.LabelOpts(rotate=30, interval=0, font_size=10,
                                                                   font_weight="bold")),
            yaxis_opts=opts.AxisOpts(
                name=info[0],
                min_=0,
                max_=max(data[1]) * 1.2,
                position="left",
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(color="#5793f3")
                ),
                axislabel_opts=opts.LabelOpts(formatter="{value}"),
            ),
            title_opts=opts.TitleOpts(title=info[1]),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
        )
    )
    line = (
        Line()
            .add_xaxis(x_data)
            .add_yaxis(
            "次数",
            data[2],
            yaxis_index=1,
            color="#675bba",
            label_opts=opts.LabelOpts(is_show=False),
            linestyle_opts=opts.LineStyleOpts(width=4, opacity=1)
        )

    )

    bar.overlap(line)
    return Grid().add(bar, opts.GridOpts(pos_left="5%", pos_right="20%"), is_control_axis_index=True)


regions_available = [
                    "2012-2019中国最具幸福感城市前10排行榜",
                    "2010-2016中国分省互联网普及率",
                    "近19年浙江省和天津市GDP对比",
                    "近7年浙江省和天津市互联网普及率对比",
                     "近6年浙江省和天津市电商销售额对比"]

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home_page():
    return render_template('results1.html',
                           the_select_region=regions_available)

@app.route('/subpage', methods=['POST'])
def run_select():
    the_region = request.form["the_region_selected"]
    logger.debug(the_region)  # 检查用户输入
    data = [list(dfh.province)]
    logger.debug(data)
    if the_region == regions_available[0]:
        plot_all = scatter()
        data_str = dfh.to_html()
        return render_template('results2.html',
                               the_plot_all=plot_all,
                               the_res=data_str,
                               the_select_region=regions_available)
    elif the_region == regions_available[1]:
        # 互联网普及率2016-2010
        c = Timeline()
        for i in range(2010, 2017):
            map = (
                Map()
                    .add("互联网普及率", list(zip(dfi['province'], dfi['year_{}'.format(i)])), "china", is_map_symbol_show=False)
                    .set_global_opts(
                    title_opts=opts.TitleOpts(title="{}中国分省互联网普及率热力图".format(i), subtitle="",
                                              subtitle_textstyle_opts=opts.TextStyleOpts(color="blue", font_size=18)),
                    visualmap_opts=opts.VisualMapOpts(min_=0, max_=110, series_index=0),
                )
            )
            c.add(map, "{}".format(i))
        data_str = dfi.to_html()
        return render_template('results2.html',
                               the_plot_all=c.render_embed(),
                               the_res=data_str,
                               the_select_region=regions_available)
    elif the_region == regions_available[2]:
        dfcg = pd.read_csv("compare_GDP.csv")
        data_str = dfcg.to_html()
        data = compare_GDP(data=dfcg)
        return render_template('results3.html',
                               data=data,
                               the_res=data_str,
                               the_select_region=regions_available)

    elif the_region == regions_available[3]:
        dfci = pd.read_csv("compare_internet.csv")
        data_str = dfci.to_html()
        data = compare_internet(dfci)
        pprint(data)
        return render_template('results4.html',
                               data=data,
                               the_res=data_str,
                               the_select_region=regions_available)
    elif the_region == regions_available[4]:
        dfce = pd.read_csv("compare_E.csv")
        data_str = dfce.to_html()
        data = compare_sales(dfce)
        pprint(data)
        return render_template('results5.html',
                               data=data,
                               the_res=data_str,
                               the_select_region=regions_available)


def scatter():
    """散点图"""
    c = (
        Scatter(init_opts=opts.InitOpts(width="2500px", height="800px"))
            .add_xaxis(list(dfh.province))
            .add_yaxis("次数", list(dfh.times))
            .set_global_opts(title_opts=opts.TitleOpts(title="2012-2019最具幸福感城市推选评比上榜（前五）次数"))
    )
    return c.render_embed()

def compare_GDP(data):
    df1 = data.set_index("province")  # 把rate转化为index
    # zhejiang = go.Scatter(
    #     x=[pd.to_datetime('01/01/{y}'.format(y=x), format="%m/%d/%Y") for x in df1.columns.values],
    #     y=df1.loc["浙江省", :].values,
    #     name="浙江省")
    zhejiang = {
        'x': [str(pd.to_datetime('01/01/{y}'.format(y=x), format="%m/%d/%Y")) for x in df1.columns.values],
        'y': list(df1.loc["浙江省", :].values),
        'name': "浙江省"
    }

    # tianjin = go.Scatter(
    #     x=[pd.to_datetime('01/01/{y}'.format(y=x), format="%m/%d/%Y") for x in df1.columns.values],
    #     y=df1.loc["天津市", :].values,
    #     name="天津市"
    # )
    tianjin = {
        'x': [str(pd.to_datetime('01/01/{y}'.format(y=x), format="%m/%d/%Y")) for x in df1.columns.values],
        'y': list(df1.loc["天津市", :].values),
        'name': "天津市"
    }
    layout = dict(xaxis=dict(rangeselector=dict(buttons=list([
        dict(count=3,
             label="3年",
             step="year",
             stepmode="backward"),
        dict(count=5,
             label="5年",
             step="year",
             stepmode="backward"),
        dict(count=10,
             label="10年",
             step="year",
             stepmode="backward"),
        dict(count=20,
             label="20年",
             step="year",
             stepmode="backward"),
        dict(step="all")
    ])),
        rangeslider=dict(bgcolor="#F4FA58"),
        title='年份'
    ),
        yaxis=dict(title='亿元'),
        title="近19年浙江省和天津市GDP对比"
    )

    fig = dict(data=[zhejiang, tianjin], layout=layout)
    return fig


def compare_internet(data):
    dfcg = pd.read_csv("compare_GDP.csv")
    df1 = data.set_index("province")  # 把rate转化为index
    zhejiang = {
        'x': [str(pd.to_datetime('01/01/{y}'.format(y=x), format="%m/%d/%Y")) for x in df1.columns.values],
        'y': list(df1.loc["浙江省", :].values),
        'name': "浙江省"
    }
    tianjin = {
        'x': [str(pd.to_datetime('01/01/{y}'.format(y=x), format="%m/%d/%Y")) for x in df1.columns.values],
        'y': list(df1.loc["天津市", :].values),
        'name': "天津市"
    }
    layout = dict(xaxis=dict(rangeselector=dict(buttons=list([
        dict(count=3,
             label="3年",
             step="year",
             stepmode="backward"),
        dict(count=5,
             label="5年",
             step="year",
             stepmode="backward"),
        dict(count=10,
             label="10年",
             step="year",
             stepmode="backward"),
        dict(count=20,
             label="20年",
             step="year",
             stepmode="backward"),
        dict(step="all")
    ])),
        rangeslider=dict(bgcolor="#F4FA58"),
        title='年份'
    ),
        yaxis=dict(title='亿元'),
        title="近7年浙江省和天津市互联网普及率对比"
    )
    fig = dict(data=[zhejiang, tianjin], layout=layout)
    return fig

def compare_sales(data):
    dfce = pd.read_csv("compare_E.csv")
    df1 = data.set_index("province")  # 把rate转化为index
    zhejiang = {
        'x': [str(pd.to_datetime('01/01/{y}'.format(y=x), format="%m/%d/%Y")) for x in df1.columns.values],
        'y': list(df1.loc["浙江省", :].values),
        'name': "浙江省"
    }
    tianjin = {
        'x': [str(pd.to_datetime('01/01/{y}'.format(y=x), format="%m/%d/%Y")) for x in df1.columns.values],
        'y': list(df1.loc["天津市", :].values),
        'name': "天津市"
    }
    layout = dict(xaxis=dict(rangeselector=dict(buttons=list([
        dict(count=3,
             label="3年",
             step="year",
             stepmode="backward"),
        dict(count=5,
             label="5年",
             step="year",
             stepmode="backward"),
        dict(count=10,
             label="10年",
             step="year",
             stepmode="backward"),
        dict(count=20,
             label="20年",
             step="year",
             stepmode="backward"),
        dict(step="all")
    ])),
        rangeslider=dict(bgcolor="#F4FA58"),
        title='年份'
    ),
        yaxis=dict(title='亿元'),
        title="近6年浙江省和天津市电商销售额对比"
    )
    fig = dict(data=[zhejiang, tianjin], layout=layout)
    return fig


if __name__ == '__main__':
    app.run(debug=True, port=8000)
