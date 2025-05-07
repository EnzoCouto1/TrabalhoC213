import plotly.graph_objects as go

def plot_dataset_graph_plotly(tempo, degrau, Temp_glicerina, titulo):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=tempo, y=degrau, mode='lines', name="Degrau"))
    fig.add_trace(go.Scatter(x=tempo, y=Temp_glicerina, mode='lines', name="Temperatura da Glicerina"))
    fig.update_layout(
        xaxis_title='Tempo [s]',
        yaxis_title='Amplitude',
        title=titulo,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def plot_graph_open_loop_plotly(tempo_aberta, saida_aberta, tempo, degrau, titulo):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=tempo_aberta, y=saida_aberta, mode='lines', name="Saída em Malha Aberta"))
    fig.add_trace(go.Scatter(x=tempo, y=degrau, mode='lines', name="Degrau de Entrada", line=dict(dash='dash')))
    fig.update_layout(
        xaxis_title='Tempo [s]',
        yaxis_title='Amplitude',
        title=titulo,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def plot_graph_closed_loop_plotly(tempo_fechada, saida_fechada, tempo, degrau, titulo):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=tempo_fechada, y=saida_fechada, mode='lines', name="Saída em Malha Fechada"))
    fig.add_trace(go.Scatter(x=tempo, y=degrau, mode='lines', name="Degrau de Entrada", line=dict(dash='dash')))
    fig.update_layout(
        xaxis_title='Tempo [s]',
        yaxis_title='Amplitude',
        title=titulo,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def plot_graph_pid_plotly(tempo_res, sinal_res, tempo, Titulo, degrau):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=tempo_res, y=sinal_res, mode='lines', name=Titulo))
    fig.add_trace(go.Scatter(x=tempo_res, y=degrau, mode='lines', name='Degrau de Entrada', line=dict(dash='dash')))
    fig.update_layout(
        xaxis_title='Tempo (segundos)',
        yaxis_title='Saída',
        title=Titulo,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig