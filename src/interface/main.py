import sys
import os

# Adiciona o diretório 'src' ao sys.path para permitir imports relativos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import scipy.io  # type: ignore
import numpy as np
import control as ctl  # type: ignore
import plotly.graph_objects as go
from models.pid_model import estimate_pid_values, CHR, ITAE
from utils.plot_utils import (
    plot_dataset_graph_plotly,
    plot_graph_open_loop_plotly,
    plot_graph_closed_loop_plotly,
    plot_graph_pid_plotly,
)


def main():
    # Centralized title
    st.title("Sistema de Controle distribuído para Branqueamento Térmico da Glicerina com controlador PID")

    arquivo_mat = 'Dataset/Dataset_Grupo6.mat'
    try:
        Dados = scipy.io.loadmat(arquivo_mat)

        tempo = Dados['reactionExperiment'][0, 0]['sampleTime'][:, 0].astype(np.float64)
        degrau = Dados['reactionExperiment'][0, 0]['dataInput'][:, 0]
        potencia_motor = Dados['reactionExperiment'][0, 0]['dataOutput'][:, 0]

        amplitude_degrau = degrau[-1]  # Step amplitude

        st.subheader("Dados do circuito")

        with st.container():
            plot_title_graph_first = st.empty()  # Placeholder for the graph title
            plot_first_placeholder = st.empty()  # Placeholder for the graph

        # Initialize the graph with the default selectbox option
        graph_options = ("Dataset", "Malha aberta", "Malha fechada")
        option = st.selectbox("Escolha o gráfico:", graph_options, index=0)

        plot_title_graph_first.subheader(f"{option}")

        # Calculate and plot the open loop
        K, tau_estimado, theta_estimado = estimate_pid_values(tempo, degrau, potencia_motor)

        if option == "Dataset":
            fig_first = plot_dataset_graph_plotly(tempo, degrau, potencia_motor, "Dataset")

        elif option == "Malha aberta":
            # Create the transfer function for the open loop
            open_loop = ctl.tf([K], [tau_estimado, 1])

            # Adding the delay
            num_delay, den_delay = ctl.pade(theta_estimado, 20)
            open_loop_with_theta = ctl.series(ctl.tf(num_delay, den_delay), open_loop)

            # Simulate the step response
            tempo_open, saida_open = ctl.step_response(open_loop_with_theta, tempo)

            # Create plot for the open loop
            fig_first = plot_graph_open_loop_plotly(
                tempo_open, saida_open, tempo, degrau, "Resposta em Malha Aberta"
            )

        else:
            # Adding the delay
            num_delay, den_delay = ctl.pade(theta_estimado, 20)

            # Create the transfer function for the open loop
            open_loop = ctl.tf([K], [tau_estimado, 1])
            open_loop_with_theta = ctl.series(ctl.tf(num_delay, den_delay), open_loop)

            # Create the transfer function for the closed loop
            closed_loop = ctl.feedback(open_loop_with_theta, 1)

            # Simulate the step response
            tempo_closed, saida_closed = ctl.step_response(closed_loop, tempo)

            # Create plot for the closed loop
            fig_first = plot_graph_closed_loop_plotly(
                tempo_closed, saida_closed, tempo, degrau, "Resposta em Malha Fechada"
            )

        # Display the graph in the placeholder
        plot_first_placeholder.plotly_chart(fig_first, use_container_width=True)

        st.subheader("Gráfico do controlador PID")

        with st.container():
            plot_title_graph_second = st.empty()  # Placeholder for the graph title
            plot_second_placeholder = st.empty()  # Placeholder for the graph

        # Selectbox to choose the type of PID
        pid_options = ("CHR", "ITAE")
        option2 = st.selectbox("Especifique o Método de Sintonia:", pid_options, index=0)
        plot_title_graph_second.subheader(f"{option2}")

        st.write("Parâmetros do PID")

        k_vazio = st.empty()
        theta_vazio = st.empty()
        tau_vazio = st.empty()

        kp_chr_initial = 0.6 * tau_estimado / (K * theta_estimado) if K * theta_estimado != 0 else 0.0
        td_chr_initial = theta_estimado / 2
        ti_chr_initial = tau_estimado

        a, b, c, d, e, f = 0.965, -0.85, 0.796, -0.147, 0.308, 0.929
        kp_itae_initial = (a / K) * ((theta_estimado / tau_estimado) ** b) if K != 0 and tau_estimado != 0 else 0.0
        ti_itae_initial = tau_estimado / (c + (d * (theta_estimado / tau_estimado))) if tau_estimado != 0 else 0.0
        td_itae_initial = tau_estimado * e * ((theta_estimado / tau_estimado) ** f) if tau_estimado != 0 else 0.0

        if option2 == "CHR":
            kp = k_vazio.number_input("Ganho Proporcional (Kp)", value=kp_chr_initial)
            theta_d = theta_vazio.number_input("Tempo Derivativo (Td)", value=td_chr_initial)
            tau_i = tau_vazio.number_input("Tempo Integral (Ti)", value=ti_chr_initial)

            tempo_chr, saida_chr = CHR(kp, tau_i, theta_d, amplitude_degrau, tempo)
            fig_second = plot_graph_pid_plotly(tempo_chr, saida_chr, tempo, option2, degrau)

        elif option2 == "ITAE":
            kp = k_vazio.number_input("Ganho Proporcional (Kp)", value=kp_itae_initial)
            tau_i = tau_vazio.number_input("Tempo Integral (Ti)", value=ti_itae_initial)
            theta_d = theta_vazio.number_input("Tempo Derivativo (Td)", value=td_itae_initial)

            tempo_itae, saida_itae = ITAE(kp, tau_i, theta_d, amplitude_degrau, tempo)
            fig_second = plot_graph_pid_plotly(tempo_itae, saida_itae, tempo, option2, degrau)

        # Update the graph in the placeholder
        plot_second_placeholder.plotly_chart(fig_second, use_container_width=True)

    except FileNotFoundError:
        st.error(f"Erro: Arquivo '{arquivo_mat}' não encontrado.")
    except KeyError as e:
        st.error(f"Erro: Chave '{e}' não encontrada no arquivo '.mat'. Verifique a estrutura do arquivo.")
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar os dados: {e}")


if __name__ == "__main__":
    main()