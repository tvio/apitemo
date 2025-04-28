# projekt
nazev: "hsztest2"
id: 3
# v pripade cert true je to object s filename a password
# nacteni pres cert lekarny
cert:
  nazevSouboru: "cert.pfx"
  heslo: "heslo"
# prostredi "dev" ,"test" ,"prod"
prostredi: "test"
url: https://testapi.sukl.cz/hsz/v1/
jednotlive:
  - id: 1
    metoda: GET
    nazev: status sluzby
    uri: status

  # - id: 2
  #   metoda: POST
  #   nazev: posts
  #   uri: posts
  #   req:
  #     title: mujPost
  #     body: blabol
  #     # nacteni idecka usera z ciselniku v ciselniky
  #     userId: $value1

sekvence:
  - id: 1
    nazev:
      x
      # sekvence pro postnuti hlaseni a nacteni seznamu hlaseni
    kroky:
      - 1
      

monitor:
  server: localhost
  odesilatel: ei-noreply@sukl.cz
  emaily:
    - tomas.hajek@sukl.cz
  pocetVad: 2
  interval:
    hodnota: 1
    jendotka: hodina
  jednotlive:
    - 1
#umozni davat do requestu/parametru ciselnikove hodnoty z jinych api
# ciselniky:
#   - nazev: $value1
#     metoda: get
#     url: "https://jsonplaceholder.typicode.com/users"
#     atribut: id
#     limit: 1
