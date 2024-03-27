import csv
import networkx as nx
import json
import requests
import matplotlib.pyplot as plt

tablicaLaczy = []


def wczytajStruktureSieci(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        naglowki = next(reader)

        for wiersz in reader:
            host1, host2, nr1, nr2, odleglosc, portHost1, portHost2, bandwidth = wiersz
            tablicaLaczy.append([host1, host2, nr1, nr2, odleglosc, portHost1, portHost2, bandwidth])


def wczytajWezly():
    wezly = []
    for lacze in tablicaLaczy:
        wezly.append(lacze[0])
        wezly.append(lacze[1])
    wezly = set(wezly)
    return wezly


def wczytajWazagiLaczyzNajkrotszaTrasa():
    wagiLaczy = []
    for lacze in tablicaLaczy:
        wagiLaczy.append((lacze[0], lacze[1], int(lacze[4])))
    return wagiLaczy


def wczytajWazagiLaczyzNajszerszymiLaczami():
    wagiLaczy = []
    for lacze in tablicaLaczy:
        wagiLaczy.append((lacze[0], lacze[1], 1 / (int(lacze[7]))))
    return wagiLaczy


def utworzGraf(wezly, wagiLaczy):
    graf = nx.Graph()
    graf.add_nodes_from(wezly)
    graf.add_weighted_edges_from(wagiLaczy)
    return graf


def pokazGraf(graf):
    pos = nx.spring_layout(graf)
    nx.draw(graf, pos, with_labels=True, node_color='lightblue', font_weight='bold')
    nx.draw_networkx_edge_labels(graf, pos, edge_labels=nx.get_edge_attributes(graf, 'weight'))
    plt.show()


def znajdzSciezke(graf, host1, host2):
    sciezka = nx.dijkstra_path(graf, host1, host2)
    return sciezka


def wczytajOdUzytkownikaParametryStrumienia():
    print("Podaj pierwszego hosta:")
    host1 = input()
    print("Podaj drugiego hosta:")
    host2 = input()
    print("Podaj przepustowość jaką będzie zajmował strumień:")
    zajmowanaPrzepustowoscStrumienia = int(input())

    return host1, host2, zajmowanaPrzepustowoscStrumienia


def zamienNazweNaNumer(host):
    numerHosta = -1
    for lacze in tablicaLaczy:
        if (host not in lacze):
            continue

        if (lacze[0] == host):
            numerHosta = lacze[2]

        if (lacze[1] == host):
            numerHosta = lacze[3]

    return numerHosta


def dopasujPortOdDo(host1, host2):
    for lacze in tablicaLaczy:
        if host1 and host2 not in lacze:
            continue

        if (host1 == lacze[0]):
            return lacze[5]

        if (host1 == lacze[1]):
            return lacze[6]


def wyborFunkcji():
    print("------------------------")
    print()
    print("Aplikacja Sterująca")
    print()
    print("------------------------")
    print()
    print("Wybierz funkcję: ")
    print()
    print("1 - Dodaj strumień - Najkrótsza trasa (najmniejsze opóźnienia)")
    print("")
    print("2 - Dodaj strumień - Największa przepustowość łączy")
    print("")
    print("3 - Zakończ działanie aplikacji")
    print("")

    wybor = int(input())
    return wybor


def znajdzDostepnaPrzepustowosc(host1, host2):
    dostepnaPrzepustowosc = -1
    for lacze in tablicaLaczy:
        if (host1 in lacze and host2 in lacze):
            dostepnaPrzepustowosc = int(lacze[7])

    return dostepnaPrzepustowosc


def poczatekJson():
    with open("flows.json", "w") as file:
        file.write("{ \n \t\"flows\": [\n")


def dodajHostSwitchFirst(numerHosta):
    deviceId = "of:000000000000000" + ("a" if numerHosta == str(10) else numerHosta)
    with open("flows.json", "a") as file:
        content = {
            "priority": 40000,
            "timeout": 0,
            "isPermanent": "true",
            "deviceId": deviceId,
            "treatment": {
                "instructions": [
                    {
                        "type": "OUTPUT",
                        "port": "1"
                    }
                ]
            },
            "selector": {
                "criteria": [
                    {
                        "type": "ETH_TYPE",
                        "ethType": "0x0800"
                    },
                    {
                        "type": "IPV4_DST",
                        "ip": f"10.0.0.{numerHosta}/32"
                    }
                ]
            }
        }
        json.dump(content, file, indent=5)
        file.write(",")


def dodajHostSwitchLast(numerHosta):
    deviceId = "of:000000000000000" + ("a" if numerHosta == str(10) else numerHosta)
    with open("flows.json", "a") as file:
        content = {
            "priority": 40000,
            "timeout": 0,
            "isPermanent": "true",
            "deviceId": deviceId,
            "treatment": {
                "instructions": [
                    {
                        "type": "OUTPUT",
                        "port": "1"
                    }
                ]
            },
            "selector": {
                "criteria": [
                    {
                        "type": "ETH_TYPE",
                        "ethType": "0x0800"
                    },
                    {
                        "type": "IPV4_DST",
                        "ip": f"10.0.0.{numerHosta}/32"
                    }
                ]
            }
        }
        json.dump(content, file, indent=5)


def dodajSwitchSwitch(numerObecnegoHosta, numerNastepnegoHosta, numerOstatniegoHosta):
    deviceId = "of:000000000000000" + (
        "a" if zamienNazweNaNumer(numerObecnegoHosta) == str(10) else zamienNazweNaNumer(numerObecnegoHosta))
    with open("flows.json", "a") as file:
        content = {
            "priority": 40000,
            "timeout": 0,
            "isPermanent": "true",
            "deviceId": deviceId,
            "treatment": {
                "instructions": [
                    {
                        "type": "OUTPUT",
                        "port": dopasujPortOdDo(numerObecnegoHosta, numerNastepnegoHosta)
                    }
                ]
            },
            "selector": {
                "criteria": [
                    {
                        "type": "ETH_TYPE",
                        "ethType": "0x0800"
                    },
                    {
                        "type": "IPV4_DST",
                        "ip": f"10.0.0.{zamienNazweNaNumer(numerOstatniegoHosta)}/32"
                    }
                ]
            }
        }
        json.dump(content, file, indent=5)
        file.write(",")


def koniecJson():
    with open("flows.json", "a") as file:
        file.write("\n]\n}")


def przeslij():
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    with open('flows.json') as f:
        data = f.read()
        response = requests.post('http://192.168.56.107:8181/onos/v1/flows', headers=headers, data=data,
                                 auth=('karaf', 'karaf'))
        return response


if __name__ == "__main__":

    wczytajStruktureSieci("struktura.csv")
    wezly = wczytajWezly()

    dostepnePrzepustowosci = {}

    while (True):

        wybor = wyborFunkcji()

        if (wybor == 1):
            wagiLaczy = wczytajWazagiLaczyzNajkrotszaTrasa()
        elif (wybor == 2):
            wagiLaczy = wczytajWazagiLaczyzNajszerszymiLaczami()
        elif (wybor == 3):
            break

        graf = utworzGraf(wezly, wagiLaczy)

        host1, host2, przepustowoscStrumienia = wczytajOdUzytkownikaParametryStrumienia()

        sciezka = znajdzSciezke(graf, host1, host2)

        for i in range(0, len(sciezka) - 1):

            if frozenset({sciezka[i], sciezka[i + 1]}) not in dostepnePrzepustowosci:
                dostepnePrzepustowosci[frozenset({sciezka[i], sciezka[i + 1]})] = znajdzDostepnaPrzepustowosc(
                    (sciezka[i]), (sciezka[i + 1]))

            if (dostepnePrzepustowosci[frozenset({sciezka[i], sciezka[i + 1]})] - przepustowoscStrumienia < 0):
                for lacze in wagiLaczy:
                    if (sciezka[i] in lacze and sciezka[i + 1] in lacze):
                        wagiLaczy.remove(lacze)
            else:
                dostepnePrzepustowosci[frozenset({sciezka[i], sciezka[i + 1]})] -= przepustowoscStrumienia

        graf = utworzGraf(wezly, wagiLaczy)
        sciezka = znajdzSciezke(graf, host1, host2)

        poczatekJson()

        dopasujPortOdDo(host1, host2)

        host1num = zamienNazweNaNumer(sciezka[0])
        host2num = zamienNazweNaNumer(sciezka[-1])

        dodajHostSwitchFirst(host1num)

        for i in range(0, len(sciezka) - 1):
            dodajSwitchSwitch((sciezka[i]), (sciezka[i + 1]), (sciezka[-1]))
            dodajSwitchSwitch((sciezka[i + 1]), sciezka[i], (sciezka[0]))

        dodajHostSwitchLast(host2num)
        koniecJson()
        print(przeslij())
