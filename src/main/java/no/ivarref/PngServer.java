package no.ivarref;

import org.eclipse.jetty.server.Request;
import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.server.handler.AbstractHandler;
import org.eclipse.jetty.server.handler.HandlerList;
import org.eclipse.jetty.server.handler.ResourceHandler;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.firefox.FirefoxDriver;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.TreeSet;
import java.util.stream.Collectors;

public class PngServer {

    public static void main(String[] args) throws Exception {
        System.out.println("hello world ;-)");
        Object lock = new Object();
        Server server = new Server(8080);
        FirefoxDriver driver = new FirefoxDriver();

        server.setHandler(new HandlerList() {
            {
                addHandler(new AbstractHandler() {
                    @Override
                    public void handle(String p, Request request, HttpServletRequest httpServletRequest, HttpServletResponse response) throws IOException, ServletException {
                        if ("true".equalsIgnoreCase(request.getParameter("image"))) {
                            response.setStatus(200);
                            request.setHandled(true);
                            String url = String.join("&", new TreeSet<>(request.getParameterMap().keySet())
                                    .stream()
                                    .filter(s ->
                                            s.matches("^[a-zA-Z_]+$")
                                                    && !("image".equalsIgnoreCase(s))
                                                    && request.getParameter(s).matches("^[a-zA-Z0-9_]+$"))
                                    .map(s -> s + "=" + request.getParameter(s))
                                    .collect(Collectors.toList()));
                            System.out.println("generating image for: " + url);

                            byte[] screenShot;
                            synchronized (lock) {
                                try {
                                    driver.get("http://localhost:8000/?" + url);
                                    screenShot = driver.getScreenshotAs(OutputType.BYTES);
                                } finally {
                                    //driver.quit();
                                }
                            }
                            System.out.println("length of screenshot: " + screenShot.length);

                            response.setContentType("image/png");
                            response.setContentLength(screenShot.length);
                            response.getOutputStream().write(screenShot);
                        }
                    }
                });
                addHandler(new ResourceHandler() {
                    {
                        setResourceBase(".");
                    }
                });
            }
        });
        server.start();
        server.join();
    }
}
