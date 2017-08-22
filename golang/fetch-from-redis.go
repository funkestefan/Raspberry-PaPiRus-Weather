package main
import (
  "fmt"
  "log"
  "github.com/go-redis/redis"
)

var name_temperature string = "Temp"
var name_humidity string = "Hum"

var client = redis.NewClient(&redis.Options{
  Addr:     "localhost:6379",
  Password: "",
  DB:       0,
})


func main() {
  pong, err := client.Ping().Result()
  if(err == nil) && (pong == "PONG"){
    temperature := fetchredis(name_temperature)
    humidity := fetchredis(name_humidity)
    fmt.Println(temperature)
    fmt.Println(humidity)
  } else {
    log.Fatal(err)
  }
}

func fetchredis(val string) string{
  var fetch string = val
  vfromredis, err := client.Get(fetch).Result()
  if err != nil {
    log.Fatal(err)
  }
  return(vfromredis)
}
