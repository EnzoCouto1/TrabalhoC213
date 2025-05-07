import control as ctl  # type: ignore


def estimate_pid_values(tempo, degrau, Temp_glicerina):
    """
    Estimate PID values based on the step response of the glicerina output.

    Parameters:
    tempo (list): Time vector.
    degrau (list): Step input vector.
    Temp_glicerina (list): glicerina output response vector.

    Returns:
    tuple: Estimated values of K, tau, and theta.
    """
    # Determine the final value of the response and the amplitude of the step input
    amplitude_degrau = degrau[-1]
    valor_final = Temp_glicerina[-1]

    # Adjust the glicerina output response
    valor_final = Temp_glicerina[-1]
    K = valor_final / amplitude_degrau

    # Initialize time variables
    tempo_t1 = 0
    tempo_t2 = 0

    # Estimate tau and theta
    for i in range(len(Temp_glicerina)):
        if Temp_glicerina[i] >= 0.283 * valor_final and tempo_t1 == 0:
            tempo_t1 = tempo[i]
        if Temp_glicerina[i] >= 0.6321 * valor_final:
            tempo_t2 = tempo[i]
            break

    tau_estimado = 1.5 * (tempo_t2 - tempo_t1)
    theta_estimado = tempo_t2 - tau_estimado

    return K, tau_estimado, theta_estimado


def CHR(k, tau, theta, amplitude_degrau, tempo):
    """
    Calculate the response of the CHR controller.

    Parameters:
    k (float): System gain.
    tau (float): Time constant.
    theta (float): Time delay.
    amplitude_degrau (float): Amplitude of the step input.
    tempo (list): Time vector.

    Returns:
    tuple: Time vector and output response of the CHR controller.
    """
    # CHR controller parameters
    ti_chr = tau
    td_chr = theta / 2
    kp_chr = (0.6 * tau) / (k * theta)

    # PID controller transfer function
    pid_chr = [kp_chr * td_chr, kp_chr, kp_chr / ti_chr]
    den_chr = [1, 0]
    controlador_chr = ctl.tf(pid_chr, den_chr)

    # Add time delay to the CHR controller
    num_delay, den_delay = ctl.pade(theta, 20)
    controlador_chr_com_theta = ctl.series(
        ctl.tf(num_delay, den_delay), controlador_chr
    )
    sistema_com_theta = ctl.tf(k, [tau, 1])
    chr_completo = ctl.series(sistema_com_theta, controlador_chr_com_theta)

    # Closed-loop system with feedback
    sistema_chr_controlado = ctl.feedback(chr_completo, 1)
    tempo_chr, saida_chr = ctl.step_response(
        sistema_chr_controlado * amplitude_degrau, tempo
    )

    return tempo_chr, saida_chr


def ITAE(k, tau, theta, amplitude_degrau, tempo, tau_inicial=47.50):
    """
    Calculate the response of the ITAE controller.

    Parameters:
    k (float): System gain.
    tau (float): Time constant.
    theta (float): Time delay.
    amplitude_degrau (float): Amplitude of the step input.
    tempo (list): Time vector.
    tau_inicial (float): Initial time constant for the system (default is 47.50).

    Returns:
    tuple: Time vector and output response of the ITAE controller.
    """
    # ITAE controller parameters
    a, b, c, d, e, f = 0.965, -0.85, 0.796, -0.147, 0.308, 0.929

    kp_itae = (a / k) * ((theta / tau) ** b)
    ti_itae = tau / (c + (d * (theta / tau)))
    td_itae = tau * e * ((theta / tau) ** f)

    # PID controller transfer function
    pid_itae = [kp_itae * td_itae, kp_itae, kp_itae / ti_itae]
    den_itae = [1, 0]
    controlador_itae = ctl.tf(pid_itae, den_itae)

    # Add time delay to the ITAE controller
    num_delay, den_delay = ctl.pade(theta, 20)
    pid_itae_delay = ctl.series(ctl.tf(num_delay, den_delay), controlador_itae)

    # Closed-loop system with feedback
    sys_theta = ctl.tf(k, [tau, 1])  # <--- AQUI ESTÁ A CORREÇÃO
    itae = ctl.series(pid_itae_delay, sys_theta)
    sys_ctrl_itae = ctl.feedback(itae, 1)
    temp_ITAE, sinal_ITAE = ctl.step_response(sys_ctrl_itae * amplitude_degrau, tempo)

    return temp_ITAE, sinal_ITAE