import networkx as nx
import matplotlib.pyplot as plt


# # # MAKER # # #
class Maker():
    """
    Definisce un Maker con cui calcolare le distanze tra hashtag, per poi crearne un grafico
    """

    def calculate_distance(self, hashtag, connector, client):
        # Crea il grafico
        G = nx.Graph()
        # Lista che contiene tutti gli hashtag senza duplicati
        hashtag_list = set(hashtag)
        # Lista per contenere gli hashtag visitati del primo for-loop
        visited = []
        for i in hashtag_list:
            for j in hashtag_list:
                # Crea query con parametri gli hashtag ciclati con i, j
                # Circostanza i vero, j vero
                atbt = {"$and": [{"hashtags.name": '{}'.format(i)}, {"hashtags.name": '{}'.format(j)}]}
                # Circostanza i vero, b falso
                atbf = {"$and": [{"hashtags.name": '{}'.format(i)}, {"hashtags.name": {"$ne": '{}'.format(j)}}]}
                # Circostanza i falso, b vero
                afbt = {"$and": [{"hashtags.name": '{}'.format(j)}, {"hashtags.name": {"$ne": '{}'.format(i)}}]}
                # Evita di calcolare la distanza per lo stesso hashtag. Esempio: i = "hashtag_1", j = "hashtag_1"
                if j is not i:
                    # Controlla che il valore di j non sia già stato assunto da i. Evita di calcolare la distanza due
                    # volte, ad hashtag invertiti. Esempio: "hashtag_1 - hashtag_2" e "hashtag_2 - hashtag_1"
                    if j in visited:
                        print(i, j)
                        # Esegue le query
                        union = connector.get_distance(client, "twitter_bot_db", "tweet", atbt)
                        inters_a = connector.get_distance(client, "twitter_bot_db", "tweet", atbf)
                        inters_b = connector.get_distance(client, "twitter_bot_db", "tweet", afbt)
                        # Calcola l'intersezione tra i e j
                        intersection = inters_a + inters_b
                        # Calcola I/U, considerando che il risultato possa essere 0
                        try:
                            # tot = union / intersection
                            tot = intersection / union
                        except ZeroDivisionError:
                            tot = 0
                        weight = (i, j, tot)
                        print("Tupla: " + str(weight) + '\n')
                        with open("distances.txt", 'a', encoding='utf-8') as distances:
                            distances.write("U: " + str(union) + " --- I: " + str(intersection) + " --- Tupla: " +
                                            str(weight) + '\n')
                        # G.add_weighted_edges_from([weight])
                        # Aggiunge i nodi al grafico
                        G.add_node(i)
                        G.add_node(j)
                        # Considera i nodi che hanno una connessione tra di loro
                        if tot > 0:
                            # Collega i nodi
                            G.add_edge(i, j, weight=tot)
            # Inserisce il valore di i nella lista degli hashtag visitati
            visited.append(i)
        # Imposta la dimensione del grafico
        plt.figure(figsize=(30, 30))
        # Disegna il grafico
        nx.draw(G, with_labels=True, pos=nx.spring_layout(G, k=0.60), font_color="k", node_color="r", edge_color="g")
        # Salva il grafico come immagine
        plt.savefig("drone.png")
