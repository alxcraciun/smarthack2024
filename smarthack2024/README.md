# Smarthack 2024
💛 Echipa 4Gold 💛

### How to import the CSVs

- Place them in root in folder `/data/` 
- After this, make sure you have all CSVs correctly named:
  - `connections.csv`
  - `customers.csv`
  - `demands.csv`
  - `refineries.csv`
  - `tanks.csv`
- Optionally, you can store API keys inside `teams.csv`
- The `.gitignore` has the `/data/` folder already included so it won't be commited

### How to run Sprinboot API locally

Modify port if you can't use 8080: 
<br> `server.port=<your port>`

Don't forget to run with local profile 
<br> `mvn spring-boot:run -D spring-boot.run.profiles=local`

<br>

### Which localhost ports are used? 

http://localhost:8081/
Run Springboot Evaluator 

http://localhost:3031/
Run Vite+React frontend

http://localhost:8082/
FastAPI Server that logs requests + responses

<br>

### Documentation

- https://github.com/SmartHack2024/eval-data
- https://github.com/SmartHack2024/challenge
- http://localhost:8081/webjars/swagger-ui/index.html#/

<br>

### Technical References

- https://fastapi.tiangolo.com/#installation
- https://sap.github.io/ui5-webcomponents-react/v2/