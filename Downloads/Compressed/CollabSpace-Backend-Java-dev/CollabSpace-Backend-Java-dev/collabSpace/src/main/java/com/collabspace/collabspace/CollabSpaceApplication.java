package com.collabspace.collabspace;

import org.slf4j.LoggerFactory;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class CollabSpaceApplication {

    public static void main(String[] args) {
        SpringApplication.run(CollabSpaceApplication.class, args);
        LoggerFactory.getLogger(CollabSpaceApplication.class).info("------CollabSpaceApplication started------");
    }

}
