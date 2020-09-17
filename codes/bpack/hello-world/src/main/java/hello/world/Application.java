package hello.world;

import io.micronaut.runtime.Micronaut;

import io.micronaut.http.MediaType;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Get;

@Controller("/hello") 
class HelloController {

    @Get(produces = MediaType.TEXT_PLAIN) 
    public String index() {
        return "Hello World"; 
    }
}

public class Application {

    public static void main(String[] args) {
        Micronaut.run(Application.class);
    }
}