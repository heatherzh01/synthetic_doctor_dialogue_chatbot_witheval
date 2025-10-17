import streamlit as st
import contextlib
import json
import plotly.graph_objects as go
from src.session_evaluator import Evaluator
import sys
sys.path.append('..')


st.set_page_config(
    page_title="Welcome to NovoNordisk ChatHCP Evaluator",
    page_icon="👋",
)

llm = 'gpt-4-0125-preview'
llm_params = {'temperature': 0, 'top-p': 0, 'frequency_penalty': 0, 'seed': 1000}
evaluator = Evaluator(
    knowledge=False,
    llm=llm,
    llm_params=llm_params
)

col1, col2 = st.columns([4, 1])
with col1:
    st.markdown('''### :green[Session 评价]''')
with col2:
    if st.button('保存评价结果'):
        evaluator.save('../output/evaluation')

if st.sidebar.button('清除评分信息'):
    if 'scores' in st.session_state:
        del st.session_state['scores']

uploaded_file = st.sidebar.file_uploader("请选择对话记录", accept_multiple_files=False)
if uploaded_file:
    evaluator.set_session(uploaded_file)
    assert(evaluator.session is not None)

    if st.sidebar.button('点击查看 - 异议详情'):
        st.markdown(f'##### 参与人:')
        st.markdown(f'{evaluator.session.rep.name}')
        st.markdown(f'##### 虚拟医生:')
        st.markdown(f'\t{evaluator.session.hcp.hcp_name}医生')
        st.markdown(f'##### 异议题目:')
        st.markdown(f'\t预设异议: {evaluator.session.objection.preset_objection}')
        st.markdown(f'\t真实异议: {evaluator.session.objection.real_objection}')

    if st.sidebar.button('点击查看 - 对话内容'):
        for message in evaluator.session.chat_history:
            if message["role"] in ['user', 'assistant']:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

    if st.sidebar.button('点击评价 - C-澄清部分'):
        if 'clarify_score' not in st.session_state:
            st.session_state['clarify_score'] = {}

            evaluator.evaluate_clarify_correctness()
            st.write('clarify_correctness')
            st.write(evaluator.clarify_score['correctness'])
            st.session_state.clarify_score['correctness'] = evaluator.clarify_score['correctness']

            evaluator.evaluate_clarify_process()
            st.write('clarify_process')
            st.write(evaluator.clarify_score['process'])
            st.session_state.clarify_score['process'] = evaluator.clarify_score['process']

            evaluator.evaluate_clarify_skills()
            st.write('clarify_skills')
            st.write(evaluator.clarify_score['skills'])
            st.session_state.clarify_score['skills'] = evaluator.clarify_score['skills']
        else:
            st.write(st.session_state.clarify_score)

        if 'clarify_score' in st.session_state:
            ## Customization
            with st.sidebar:
                with st.expander("Customization options"):
                    opacity = st.slider(
                        label="Opacity",
                        min_value=0.0,
                        max_value=1.0,
                        value=1.0,
                        step=0.1,
                        help="Sets the opacity of the trace",
                        key="opacity",
                    )

                    mode = st.multiselect(
                        label="Mode",
                        options=["lines", "markers"],
                        default=["lines", "markers"],
                        help='Determines the drawing mode for this scatter trace. If the provided `mode` includes "text" then the `text` elements appear at the coordinates. '
                             'Otherwise, the `text` elements appear on hover. If there are less than 20 points and the trace is not stacked then the default is "lines+markers". Otherwise, "lines".',
                        key="mode",
                    )

                    hovertemplate = st.text_input(
                        label="Hover template",
                        value="%{theta}: %{r}",
                        help=r"""Template string used for rendering the information that appear on hover box. Note that this will override `hoverinfo`.
                        Variables are inserted using %{variable}, for example "y: %{y}" as well as %{xother}, {%_xother}, {%_xother_}, {%xother_}.
                        When showing info for several points, "xother" will be added to those with different x positions from the first point.
                        An underscore before or after "(x|y)other" will add a space on that side, only when this field is shown.
                        Numbers are formatted using d3-format's syntax %{variable:d3-format}, for example "Price: %{y:$.2f}".
                        https://github.com/d3/d3-format/tree/v1.4.5#d3-format for details on the formatting syntax.
                        Dates are formatted using d3-time-format's syntax %{variable|d3-time-format}, for example "Day: %{2019-01-01|%A}".
                        https://github.com/d3/d3-time-format/tree/v2.2.3#locale_format for details on the date formatting syntax.
                        The variables available in `hovertemplate` are the ones emitted as event data described at this link https://plotly.com/javascript/plotlyjs-events/#event-data.
                        Additionally, every attributes that can be specified per-point (the ones that are `arrayOk: True`) are available.
                        Anything contained in tag `<extra>` is displayed in the secondary box, for example "<extra>{fullData.name}</extra>".
                        To hide the secondary box completely, use an empty tag `<extra></extra>`.""",
                        key="hovertemplate",
                    )

                    marker_color = st.color_picker(
                        label="Marker color",
                        value="#636EFA",
                        key="marker_color",
                        help="Sets the marker color",
                    )

                    marker_opacity = st.slider(
                        label="Marker opacity",
                        min_value=0.0,
                        max_value=1.0,
                        value=1.0,
                        step=0.1,
                        help="Sets the marker opacity",
                        key="marker_opacity",
                    )

                    marker_size = st.slider(
                        label="Marker size",
                        min_value=0,
                        max_value=10,
                        value=6,
                        step=1,
                        help="Sets the marker size (in px)",
                        key="marker_size",
                    )

                    marker_symbol = st.selectbox(
                        label="Marker symbol",
                        index=24,
                        options=[
                            "arrow",
                            "arrow-bar-down",
                            "arrow-bar-down-open",
                            "arrow-bar-left",
                            "arrow-bar-left-open",
                            "arrow-bar-right",
                            "arrow-bar-right-open",
                            "arrow-bar-up",
                            "arrow-bar-up-open",
                            "arrow-down",
                            "arrow-down-open",
                            "arrow-left",
                            "arrow-left-open",
                            "arrow-open",
                            "arrow-right",
                            "arrow-right-open",
                            "arrow-up",
                            "arrow-up-open",
                            "arrow-wide",
                            "arrow-wide-open",
                            "asterisk",
                            "asterisk-open",
                            "bowtie",
                            "bowtie-open",
                            "circle",
                            "circle-cross",
                            "circle-cross-open",
                            "circle-dot",
                            "circle-open",
                            "circle-open-dot",
                            "circle-x",
                            "circle-x-open",
                            "cross",
                            "cross-dot",
                            "cross-open",
                            "cross-open-dot",
                            "cross-thin",
                            "cross-thin-open",
                            "diamond",
                            "diamond-cross",
                            "diamond-cross-open",
                            "diamond-dot",
                            "diamond-open",
                            "diamond-open-dot",
                            "diamond-tall",
                            "diamond-tall-dot",
                            "diamond-tall-open",
                            "diamond-tall-open-dot",
                            "diamond-wide",
                            "diamond-wide-dot",
                            "diamond-wide-open",
                            "diamond-wide-open-dot",
                            "diamond-x",
                            "diamond-x-open",
                            "hash",
                            "hash-dot",
                            "hash-open",
                            "hash-open-dot",
                            "hexagon",
                            "hexagon2",
                            "hexagon2-dot",
                            "hexagon2-open",
                            "hexagon2-open-dot",
                            "hexagon-dot",
                            "hexagon-open",
                            "hexagon-open-dot",
                            "hexagram",
                            "hexagram-dot",
                            "hexagram-open",
                            "hexagram-open-dot",
                            "hourglass",
                            "hourglass-open",
                            "line-ew",
                            "line-ew-open",
                            "line-ne",
                            "line-ne-open",
                            "line-ns",
                            "line-ns-open",
                            "line-nw",
                            "line-nw-open",
                            "octagon",
                            "octagon-dot",
                            "octagon-open",
                            "octagon-open-dot",
                            "pentagon",
                            "pentagon-dot",
                            "pentagon-open",
                            "pentagon-open-dot",
                            "square",
                            "square-cross",
                            "square-cross-open",
                            "square-dot",
                            "square-open",
                            "square-open-dot",
                            "square-x",
                            "square-x-open",
                            "star",
                            "star-diamond",
                            "star-diamond-dot",
                            "star-diamond-open",
                            "star-diamond-open-dot",
                            "star-dot",
                            "star-open",
                            "star-open-dot",
                            "star-square",
                            "star-square-dot",
                            "star-square-open",
                            "star-square-open-dot",
                            "star-triangle-down",
                            "star-triangle-down-dot",
                            "star-triangle-down-open",
                            "star-triangle-down-open-dot",
                            "star-triangle-up",
                            "star-triangle-up-dot",
                            "star-triangle-up-open",
                            "star-triangle-up-open-dot",
                            "triangle-down",
                            "triangle-down-dot",
                            "triangle-down-open",
                            "triangle-down-open-dot",
                            "triangle-left",
                            "triangle-left-dot",
                            "triangle-left-open",
                            "triangle-left-open-dot",
                            "triangle-ne",
                            "triangle-ne-dot",
                            "triangle-ne-open",
                            "triangle-ne-open-dot",
                            "triangle-nw",
                            "triangle-nw-dot",
                            "triangle-nw-open",
                            "triangle-nw-open-dot",
                            "triangle-right",
                            "triangle-right-dot",
                            "triangle-right-open",
                            "triangle-right-open-dot",
                            "triangle-se",
                            "triangle-se-dot",
                            "triangle-se-open",
                            "triangle-se-open-dot",
                            "triangle-sw",
                            "triangle-sw-dot",
                            "triangle-sw-open",
                            "triangle-sw-open-dot",
                            "triangle-up",
                            "triangle-up-dot",
                            "triangle-up-open",
                            "triangle-up-open-dot",
                            "x",
                            "x-dot",
                            "x-open",
                            "x-open-dot",
                            "x-thin",
                            "x-thin-open",
                            "y-down",
                            "y-down-open",
                            "y-left",
                            "y-left-open",
                            "y-right",
                            "y-right-open",
                            "y-up",
                            "y-up-open",
                        ],
                        help="""Sets the marker symbol type. Adding 100 is equivalent to appending "-open" to a symbol name.
                        Adding 200 is equivalent to appending "-dot" to a symbol name. Adding 300 is equivalent to appending "-open-dot" or "dot-open" to a symbol name.""",
                        key="marker_symbol",
                    )

                    line_color = st.color_picker(
                        label="Line color",
                        value="#636EFA",
                        key="line_color",
                        help="Sets the line color",
                    )

                    line_dash = st.selectbox(
                        label="Line dash",
                        options=["solid", "dot", "dash", "longdash", "dashdot", "longdashdot"],
                        help="""Sets the dash style of lines.
                        Set to a dash type string ("solid", "dot", "dash", "longdash", "dashdot", or "longdashdot") or a dash length list in px (eg "5px,10px,2px,2px").""",
                        key="line_dash",
                    )

                    line_shape = st.selectbox(
                        label="Line shape",
                        options=["linear", "spline"],
                        help="""Determines the line shape. With "spline" the lines are drawn using spline interpolation.
                        The other available values correspond to step-wise line shapes.""",
                        key="line_shape",
                    )

                    line_smoothing = st.slider(
                        label="Line smoothing",
                        min_value=0.0,
                        max_value=1.3,
                        value=1.0,
                        step=0.1,
                        help="""Has an effect only if `shape` is set to "spline" Sets the amount of smoothing.
                        "0" corresponds to no smoothing (equivalent to a "linear" shape).""",
                        key="line_smoothing",
                        disabled=line_shape == "linear",
                    )

                    line_width = st.slider(
                        label="Line width",
                        min_value=0,
                        max_value=10,
                        value=2,
                        step=1,
                        help="""Sets the line width (in px).""",
                        key="line_width",
                    )

                    fillcolor = st.color_picker(
                        label="Fill color",
                        value="#636EFA",
                        key="fillcolor",
                        help="Sets the fill color. Defaults to a half-transparent variant of the line color, marker color, or marker line color, whichever is available.",
                    )

                    fill_opacity = st.slider(
                        label="Fill opacity",
                        min_value=0.0,
                        max_value=1.0,
                        value=0.5,
                        step=0.1,
                        help="""Sets the fill opacity.""",
                        key="fill_opacity",
                    )

                    rgba = tuple(
                        (
                                [int(fillcolor.lstrip("#")[i: i + 2], 16) for i in (0, 2, 4)]
                                + [fill_opacity]
                        )
                    )

            # Radar plot
            with contextlib.suppress(IndexError, NameError):
                labels = ['准确性', '流程'] + list(st.session_state.clarify_score['skills'].keys())
                values = [float(st.session_state.clarify_score['correctness']['score']), float(st.session_state.clarify_score['process']['score'])] + \
                         [float(st.session_state.clarify_score['skills'][x]['score']) for x in st.session_state.clarify_score['skills']]
                labels = (labels + [labels[0]])[::-1]
                values = (values + [values[0]])[::-1]

                data = go.Scatterpolar(
                    r=values,
                    theta=labels,
                    mode="none" if mode == [] else "+".join(mode),
                    opacity=opacity,
                    hovertemplate=hovertemplate + "<extra></extra>",
                    marker_color=marker_color,
                    marker_opacity=marker_opacity,
                    marker_size=marker_size,
                    marker_symbol=marker_symbol,
                    line_color=line_color,
                    line_dash=line_dash,
                    line_shape=line_shape,
                    line_smoothing=line_smoothing,
                    line_width=line_width,
                    fill="toself",
                    fillcolor=f"RGBA{rgba}" if rgba else "RGBA(99, 110, 250, 0.5)",
                )

                layout = go.Layout(
                    title=dict(
                        text="医药代表技能雷达图 [C-澄清部分]",
                        x=0.5,
                        xanchor="center",
                    ),
                    paper_bgcolor="rgba(100,100,100,0)",
                    plot_bgcolor="rgba(100,100,100,0)",
                )

                fig = go.Figure(data=data, layout=layout)

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    sharing="streamlit",
                    theme="streamlit",
                )

            st.markdown('###### C-澄清部分 - 技巧 子维度评价明细')
            st.write(st.session_state.clarify_score['skills'])

    if st.sidebar.button('点击评价 - T-解决部分'):
        if 'take_action_score' not in st.session_state:
            st.session_state['take_action_score'] = {}

            evaluator.evaluate_take_action_correctness()
            st.write('take_action_correctness')
            st.write(evaluator.take_action_score['correctness'])
            st.session_state.take_action_score['correctness'] = evaluator.take_action_score['correctness']

            evaluator.evaluate_take_action_process()
            st.write('take_action_process')
            st.write(evaluator.take_action_score['process'])
            st.session_state.take_action_score['process'] = evaluator.take_action_score['process']

            evaluator.evaluate_take_action_skills()
            st.write('take_action_skills')
            st.write(evaluator.take_action_score['skills'])
            st.session_state.take_action_score['skills'] = evaluator.take_action_score['skills']
        else:
            st.write(st.session_state.take_action_score)

        if 'take_action_score' in st.session_state:
            with st.sidebar:
                with st.expander("Customization options"):
                    opacity = st.slider(
                        label="Opacity",
                        min_value=0.0,
                        max_value=1.0,
                        value=1.0,
                        step=0.1,
                        help="Sets the opacity of the trace",
                        key="opacity",
                    )

                    mode = st.multiselect(
                        label="Mode",
                        options=["lines", "markers"],
                        default=["lines", "markers"],
                        help='Determines the drawing mode for this scatter trace. If the provided `mode` includes "text" then the `text` elements appear at the coordinates. '
                             'Otherwise, the `text` elements appear on hover. If there are less than 20 points and the trace is not stacked then the default is "lines+markers". Otherwise, "lines".',
                        key="mode",
                    )

                    hovertemplate = st.text_input(
                        label="Hover template",
                        value="%{theta}: %{r}",
                        help=r"""Template string used for rendering the information that appear on hover box. Note that this will override `hoverinfo`.
                        Variables are inserted using %{variable}, for example "y: %{y}" as well as %{xother}, {%_xother}, {%_xother_}, {%xother_}.
                        When showing info for several points, "xother" will be added to those with different x positions from the first point.
                        An underscore before or after "(x|y)other" will add a space on that side, only when this field is shown.
                        Numbers are formatted using d3-format's syntax %{variable:d3-format}, for example "Price: %{y:$.2f}".
                        https://github.com/d3/d3-format/tree/v1.4.5#d3-format for details on the formatting syntax.
                        Dates are formatted using d3-time-format's syntax %{variable|d3-time-format}, for example "Day: %{2019-01-01|%A}".
                        https://github.com/d3/d3-time-format/tree/v2.2.3#locale_format for details on the date formatting syntax.
                        The variables available in `hovertemplate` are the ones emitted as event data described at this link https://plotly.com/javascript/plotlyjs-events/#event-data.
                        Additionally, every attributes that can be specified per-point (the ones that are `arrayOk: True`) are available.
                        Anything contained in tag `<extra>` is displayed in the secondary box, for example "<extra>{fullData.name}</extra>".
                        To hide the secondary box completely, use an empty tag `<extra></extra>`.""",
                        key="hovertemplate",
                    )

                    marker_color = st.color_picker(
                        label="Marker color",
                        value="#636EFA",
                        key="marker_color",
                        help="Sets the marker color",
                    )

                    marker_opacity = st.slider(
                        label="Marker opacity",
                        min_value=0.0,
                        max_value=1.0,
                        value=1.0,
                        step=0.1,
                        help="Sets the marker opacity",
                        key="marker_opacity",
                    )

                    marker_size = st.slider(
                        label="Marker size",
                        min_value=0,
                        max_value=10,
                        value=6,
                        step=1,
                        help="Sets the marker size (in px)",
                        key="marker_size",
                    )

                    marker_symbol = st.selectbox(
                        label="Marker symbol",
                        index=24,
                        options=[
                            "arrow",
                            "arrow-bar-down",
                            "arrow-bar-down-open",
                            "arrow-bar-left",
                            "arrow-bar-left-open",
                            "arrow-bar-right",
                            "arrow-bar-right-open",
                            "arrow-bar-up",
                            "arrow-bar-up-open",
                            "arrow-down",
                            "arrow-down-open",
                            "arrow-left",
                            "arrow-left-open",
                            "arrow-open",
                            "arrow-right",
                            "arrow-right-open",
                            "arrow-up",
                            "arrow-up-open",
                            "arrow-wide",
                            "arrow-wide-open",
                            "asterisk",
                            "asterisk-open",
                            "bowtie",
                            "bowtie-open",
                            "circle",
                            "circle-cross",
                            "circle-cross-open",
                            "circle-dot",
                            "circle-open",
                            "circle-open-dot",
                            "circle-x",
                            "circle-x-open",
                            "cross",
                            "cross-dot",
                            "cross-open",
                            "cross-open-dot",
                            "cross-thin",
                            "cross-thin-open",
                            "diamond",
                            "diamond-cross",
                            "diamond-cross-open",
                            "diamond-dot",
                            "diamond-open",
                            "diamond-open-dot",
                            "diamond-tall",
                            "diamond-tall-dot",
                            "diamond-tall-open",
                            "diamond-tall-open-dot",
                            "diamond-wide",
                            "diamond-wide-dot",
                            "diamond-wide-open",
                            "diamond-wide-open-dot",
                            "diamond-x",
                            "diamond-x-open",
                            "hash",
                            "hash-dot",
                            "hash-open",
                            "hash-open-dot",
                            "hexagon",
                            "hexagon2",
                            "hexagon2-dot",
                            "hexagon2-open",
                            "hexagon2-open-dot",
                            "hexagon-dot",
                            "hexagon-open",
                            "hexagon-open-dot",
                            "hexagram",
                            "hexagram-dot",
                            "hexagram-open",
                            "hexagram-open-dot",
                            "hourglass",
                            "hourglass-open",
                            "line-ew",
                            "line-ew-open",
                            "line-ne",
                            "line-ne-open",
                            "line-ns",
                            "line-ns-open",
                            "line-nw",
                            "line-nw-open",
                            "octagon",
                            "octagon-dot",
                            "octagon-open",
                            "octagon-open-dot",
                            "pentagon",
                            "pentagon-dot",
                            "pentagon-open",
                            "pentagon-open-dot",
                            "square",
                            "square-cross",
                            "square-cross-open",
                            "square-dot",
                            "square-open",
                            "square-open-dot",
                            "square-x",
                            "square-x-open",
                            "star",
                            "star-diamond",
                            "star-diamond-dot",
                            "star-diamond-open",
                            "star-diamond-open-dot",
                            "star-dot",
                            "star-open",
                            "star-open-dot",
                            "star-square",
                            "star-square-dot",
                            "star-square-open",
                            "star-square-open-dot",
                            "star-triangle-down",
                            "star-triangle-down-dot",
                            "star-triangle-down-open",
                            "star-triangle-down-open-dot",
                            "star-triangle-up",
                            "star-triangle-up-dot",
                            "star-triangle-up-open",
                            "star-triangle-up-open-dot",
                            "triangle-down",
                            "triangle-down-dot",
                            "triangle-down-open",
                            "triangle-down-open-dot",
                            "triangle-left",
                            "triangle-left-dot",
                            "triangle-left-open",
                            "triangle-left-open-dot",
                            "triangle-ne",
                            "triangle-ne-dot",
                            "triangle-ne-open",
                            "triangle-ne-open-dot",
                            "triangle-nw",
                            "triangle-nw-dot",
                            "triangle-nw-open",
                            "triangle-nw-open-dot",
                            "triangle-right",
                            "triangle-right-dot",
                            "triangle-right-open",
                            "triangle-right-open-dot",
                            "triangle-se",
                            "triangle-se-dot",
                            "triangle-se-open",
                            "triangle-se-open-dot",
                            "triangle-sw",
                            "triangle-sw-dot",
                            "triangle-sw-open",
                            "triangle-sw-open-dot",
                            "triangle-up",
                            "triangle-up-dot",
                            "triangle-up-open",
                            "triangle-up-open-dot",
                            "x",
                            "x-dot",
                            "x-open",
                            "x-open-dot",
                            "x-thin",
                            "x-thin-open",
                            "y-down",
                            "y-down-open",
                            "y-left",
                            "y-left-open",
                            "y-right",
                            "y-right-open",
                            "y-up",
                            "y-up-open",
                        ],
                        help="""Sets the marker symbol type. Adding 100 is equivalent to appending "-open" to a symbol name.
                        Adding 200 is equivalent to appending "-dot" to a symbol name. Adding 300 is equivalent to appending "-open-dot" or "dot-open" to a symbol name.""",
                        key="marker_symbol",
                    )

                    line_color = st.color_picker(
                        label="Line color",
                        value="#636EFA",
                        key="line_color",
                        help="Sets the line color",
                    )

                    line_dash = st.selectbox(
                        label="Line dash",
                        options=["solid", "dot", "dash", "longdash", "dashdot", "longdashdot"],
                        help="""Sets the dash style of lines.
                        Set to a dash type string ("solid", "dot", "dash", "longdash", "dashdot", or "longdashdot") or a dash length list in px (eg "5px,10px,2px,2px").""",
                        key="line_dash",
                    )

                    line_shape = st.selectbox(
                        label="Line shape",
                        options=["linear", "spline"],
                        help="""Determines the line shape. With "spline" the lines are drawn using spline interpolation.
                        The other available values correspond to step-wise line shapes.""",
                        key="line_shape",
                    )

                    line_smoothing = st.slider(
                        label="Line smoothing",
                        min_value=0.0,
                        max_value=1.3,
                        value=1.0,
                        step=0.1,
                        help="""Has an effect only if `shape` is set to "spline" Sets the amount of smoothing.
                        "0" corresponds to no smoothing (equivalent to a "linear" shape).""",
                        key="line_smoothing",
                        disabled=line_shape == "linear",
                    )

                    line_width = st.slider(
                        label="Line width",
                        min_value=0,
                        max_value=10,
                        value=2,
                        step=1,
                        help="""Sets the line width (in px).""",
                        key="line_width",
                    )

                    fillcolor = st.color_picker(
                        label="Fill color",
                        value="#636EFA",
                        key="fillcolor",
                        help="Sets the fill color. Defaults to a half-transparent variant of the line color, marker color, or marker line color, whichever is available.",
                    )

                    fill_opacity = st.slider(
                        label="Fill opacity",
                        min_value=0.0,
                        max_value=1.0,
                        value=0.5,
                        step=0.1,
                        help="""Sets the fill opacity.""",
                        key="fill_opacity",
                    )

                    rgba = tuple(
                        (
                                [int(fillcolor.lstrip("#")[i: i + 2], 16) for i in (0, 2, 4)]
                                + [fill_opacity]
                        )
                    )

            # Radar plot
            with contextlib.suppress(IndexError, NameError):
                labels = ['准确性', '流程'] + list(st.session_state.take_action_score['skills'].keys())
                values = [float(st.session_state.take_action_score['correctness']['score']),
                          float(st.session_state.take_action_score['process']['score'])] + \
                         [float(st.session_state.take_action_score['skills'][x]['score']) for x in
                          st.session_state.take_action_score['skills']]
                labels = (labels + [labels[0]])[::-1]
                values = (values + [values[0]])[::-1]

                data = go.Scatterpolar(
                    r=values,
                    theta=labels,
                    mode="none" if mode == [] else "+".join(mode),
                    opacity=opacity,
                    hovertemplate=hovertemplate + "<extra></extra>",
                    marker_color=marker_color,
                    marker_opacity=marker_opacity,
                    marker_size=marker_size,
                    marker_symbol=marker_symbol,
                    line_color=line_color,
                    line_dash=line_dash,
                    line_shape=line_shape,
                    line_smoothing=line_smoothing,
                    line_width=line_width,
                    fill="toself",
                    fillcolor=f"RGBA{rgba}" if rgba else "RGBA(99, 110, 250, 0.5)",
                )

                layout = go.Layout(
                    title=dict(
                        text="医药代表技能雷达图 [C-澄清部分]",
                        x=0.5,
                        xanchor="center",
                    ),
                    paper_bgcolor="rgba(100,100,100,0)",
                    plot_bgcolor="rgba(100,100,100,0)",
                )

                fig = go.Figure(data=data, layout=layout)

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    sharing="streamlit",
                    theme="streamlit",
                )

        st.markdown('###### T-解决部分 - 技巧 子维度评价明细')
        st.write(st.session_state.take_action_score['skills'])
