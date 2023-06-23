import paramiko
import tkinter as tk
from tkinter import messagebox

# Informações de conexão SSH
ip = 'olt-ip'
usuario = 'your-username'
senha = 'your-password'

# Função para executar o código quando o botão "Executar" for pressionado
def executar_ssh():
    # Obter o valor do login do cliente do campo de entrada
    login_cliente = entry_login.get()

    # Comandos a serem executados
    comandos = [
        'enable',
        'config',
        'display current-configuration'
    ]

    try:
        # Estabelecer conexão SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=usuario, password=senha)

        # Executar comandos
        for comando in comandos:
            stdin, stdout, stderr = ssh.exec_command(comando)
            output = stdout.read().decode('utf-8')
            print(output)

            # Procurar ont-lineprofile-id e service-port
            if 'ont add' in output and login_cliente in output:
                linhas = output.split('\n')
                for linha in linhas:
                    if 'ont add' in linha and login_cliente in linha:
                        elementos = linha.split()
                        ont_lineprofile_id = int(elementos[elementos.index('ont-lineprofile-id') + 1])
                        provisionamento_id = elementos[2] + ' ' + elementos[3]
                    elif 'service-port' in linha and 'ont' in linha:
                        elementos = linha.split()
                        service_port = int(elementos[1])
                        break

        # Determinar interface GPON baseado em ont-lineprofile-id
        if ont_lineprofile_id in [100, 200]:
            interface_gpon = 'gpon 0/1'
        elif ont_lineprofile_id in [300, 400]:
            interface_gpon = 'gpon 0/2'
        else:
            interface_gpon = None

        # Exibir os dados obtidos
        result_ont_lineprofile_id.config(text='ont-lineprofile-id: ' + str(ont_lineprofile_id))
        result_interface_gpon.config(text='Interface GPON: ' + str(interface_gpon))
        result_provisionamento_id.config(text='Provisionamento ID: ' + str(provisionamento_id))
        result_service_port.config(text='Service Port: ' + str(service_port))

        # Executar ações finais
        if interface_gpon is not None:
            # Desfazer a service-port
            desfazer_service_port = f'undo service-port {service_port}'
            stdin, stdout, stderr = ssh.exec_command(desfazer_service_port)
            print(stdout.read().decode('utf-8'))

            # Configurar a nova interface GPON
            configurar_interface_gpon = f'interface {interface_gpon}'
            stdin, stdout, stderr = ssh.exec_command(configurar_interface_gpon)
            print(stdout.read().decode('utf-8'))

            # Excluir o provisionamento
            excluir_provisionamento = f'ont delete {provisionamento_id}'
            stdin, stdout, stderr = ssh.exec_command(excluir_provisionamento)
            print(stdout.read().decode('utf-8'))

            # Salvar as alterações
            salvar_configuracao = 'save'
            stdin, stdout, stderr = ssh.exec_command(salvar_configuracao)
            print(stdout.read().decode('utf-8'))

        # Fechar a conexão SSH
        ssh.close()
    except Exception as e:
        messagebox.showerror('Erro', str(e))

# Criar a janela da GUI
window = tk.Tk()
window.title('Acesso SSH')
window.geometry('400x300')

# Campo de entrada para o login do cliente
label_login = tk.Label(window, text='Login do Cliente:')
label_login.pack()
entry_login = tk.Entry(window)
entry_login.pack()

# Botão de execução
button_executar = tk.Button(window, text='Executar', command=executar_ssh)
button_executar.pack()

# Resultados
result_ont_lineprofile_id = tk.Label(window, text='')
result_ont_lineprofile_id.pack()

result_interface_gpon = tk.Label(window, text='')
result_interface_gpon.pack()

result_provisionamento_id = tk.Label(window, text='')
result_provisionamento_id.pack()

result_service_port = tk.Label(window, text='')
result_service_port.pack()

# Iniciar a GUI
window.mainloop()
