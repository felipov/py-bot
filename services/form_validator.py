class FormValidator:
    """
    Serviço de validação do formulário de recrutamento
    """
    def clean(self, player_tag: str, phone: str) -> tuple[str, str]:
        """
        Limpa e formata os dados de ID e telefone enviados no formulário.

        Parameters
        ----------
        player_tag : str
            ID do jogador.
        phone : str
            Número de telefone.
        
        Returns
        -------
        tuple[str, str]
            Uma tupla contendo (player_tag, phone) formatados.
        """
        if player_tag.startswith("#"):
            player_tag = player_tag[1:]
        player_tag = player_tag.upper()
        phone = "".join(char for char in phone if char.isdigit())

        return player_tag, phone

    def validate(self, phone: str) -> str:
        """
        Valida o número de telefone.

        Parameters
        ----------
        phone : str
            Número de telefone.

        Returns
        -------
        str
            Mensagem de erro ou string vazia.
        """
        if len(phone) != 11:
            return "O telefone deve conter 11 dígitos: DDD + 9 + NUM"
        return ""