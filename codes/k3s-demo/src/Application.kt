package ch.ergonomics

import io.ktor.application.*
import io.ktor.response.*
import io.ktor.request.*
import io.ktor.features.*
import org.slf4j.event.*
import io.ktor.routing.*
import io.ktor.http.*

fun main(args: Array<String>): Unit = io.ktor.server.netty.EngineMain.main(args)

@Suppress("unused") // Referenced in application.conf
@kotlin.jvm.JvmOverloads
fun Application.module(testing: Boolean = false) {
    install(CallLogging) {
        level = Level.INFO
        filter { call -> call.request.path().startsWith("/") }
    }

    routing {
        get("/") {
            call.respondText("Hello, World!\r\n", contentType = ContentType.Text.Plain)
        }
        get("/{name}") {
            call.respondText("Hello ${call.parameters["name"]}!", contentType = ContentType.Text.Plain)
        }
    }
}

