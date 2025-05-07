import streamlit as st
import control as ctl  # type: ignore
from models.pid_model import estimate_pid_values, CHR, ITAE
from utils.plot_utils import (
    plot_dataset_graph,
    plot_graph_open_loop,
    plot_graph_closed_loop,
    plot_graph_pid,
)

st.title("Interface de Análise do Sistema")

# *** Dados do circuito ***
st.subheader("Dados do circuito")
with st.expander("Mostrar dados de teste"):
    num_points = st.number_input("Número de pontos:", min_value=50, max_value=2000, value=100)
    step_time = st.number_input("Tempo do degrau:", min_value=0.0, value=5.0)
    amplitude = st.number_input("Amplitude do degrau:", min_value=0.1, value=1.0)
    time_limit = st.number_input("Tempo total de simulação:", min_value=10.0, value=20.0)

    tempo = [i * (time_limit / num_points) for i in range(num_points)]
    degrau = [amplitude if t >= step_time else 0.0 for t in tempo]
    # Simulação simplificada da temperatura da glicerina (substitua pela sua lógica real)
    tau_real = st.number_input("Constante de tempo real (tau):", min_value=0.1, value=10.0)
    ganho_real = st.number_input("Ganho real (K):", min_value=0.01, value=0.5)
    atraso_real = st.number_input("Atraso real (theta):", min_value=0.0, value=1.0)
    Temp_glicerina = [0.0] * num_points
    for i, t in enumerate(tempo):
        if t >= atraso_real:
            Temp_glicerina[i] = ganho_real * amplitude * (1 - (2.718**(-(t - atraso_real) / tau_real)))

amplitude_degrau = amplitude  # Usando a amplitude definida acima

# *** Gráfico dos dados do circuito ***
st.subheader("Gráfico dos dados do circuito")
with st.container(height=350):
    plot_title_graph_first = st.empty()
    plot_first_placeholder = st.empty()

graph_options = ("Dataset", "Malha aberta", "Malha fechada")
option = st.selectbox("Escolha o gráfico:", graph_options, index=0)

plot_title_graph_first.subheader(f"{option}")

# Calcular e plotar a malha aberta
K, tau_estimado, theta_estimado = estimate_pid_values(tempo, degrau, Temp_glicerina)

if option == "Dataset":
    fig_first = plot_dataset_graph(tempo, degrau, Temp_glicerina, "Dataset")

elif option == "Malha aberta":
    # Criar a função de transferência para a malha aberta
    open_loop = ctl.tf([K], [tau_estimado, 1])

    # Adicionando o atraso
    num_delay, den_delay = ctl.pade(theta_estimado, 20)
    open_loop_with_theta = ctl.series(ctl.tf(num_delay, den_delay), open_loop)

    # Simular a resposta ao degrau
    tempo_open, saida_open = ctl.step_response(open_loop_with_theta, tempo)

    # Criar o gráfico para a malha aberta
    fig_first = plot_graph_open_loop(
        tempo_open, saida_open, tempo, degrau, "Resposta em Malha Aberta"
    )

else:
    # Adicionando o atraso
    num_delay, den_delay = ctl.pade(theta_estimado, 20)

    # Criar a função de transferência para a malha aberta
    open_loop = ctl.tf([K], [tau_estimado, 1])
    open_loop_with_theta = ctl.series(ctl.tf(num_delay, den_delay), open_loop)

    # Criar a função de transferência para a malha fechada
    closed_loop = ctl.feedback(open_loop_with_theta, 1)

    # Simular a resposta ao degrau
    tempo_closed, saida_closed = ctl.step_response(closed_loop, tempo)

    # Criar o gráfico para a malha fechada
    fig_first = plot_graph_closed_loop(
        tempo_closed, saida_closed, tempo, degrau, "Resposta em Malha Fechada"
    )

plot_first_placeholder.pyplot(fig_first)

# *** Gráfico do controlador PID ***
st.subheader("Gráfico do controlador PID")
with st.container(height=350):
    plot_title_graph_second = st.empty()
    plot_second_placeholder = st.empty()

pid_options = ("CHR", "ITAE")
option2 = st.selectbox("Escolha o tipo de PID:", pid_options, index=0)
plot_title_graph_second.subheader(f"{option2}")

st.write("Parâmetros do PID")

k_vazio = st.empty()
theta_vazio = st.empty()
tau_vazio = st.empty()

if option2 == "CHR":
            initial_k = 1.00
            initial_theta = 15.00
            initial_tau = 50.00

elif option2 == "ITAE":
            initial_k = 0.1
            initial_theta = 4.00
            initial_tau = 60.00

k = k_vazio.number_input("Kp", value=initial_k)
theta_d = theta_vazio.number_input("Td", value=initial_theta)
tau_i = tau_vazio.number_input("Ti", value=initial_tau)

if option2 == "CHR":
    tempo_chr, saida_chr = CHR(k, tau_i, theta_d, amplitude_degrau, tempo)
    fig_second = plot_graph_pid(tempo_chr, saida_chr, tempo, option2, degrau)

elif option2 == "ITAE":
    tempo_itae, saida_itae = ITAE(k, tau_i, theta_d, amplitude_degrau, tempo)
    fig_second = plot_graph_pid(tempo_itae, saida_itae, tempo, option2, degrau)


plot_second_placeholder.pyplot(fig_second)