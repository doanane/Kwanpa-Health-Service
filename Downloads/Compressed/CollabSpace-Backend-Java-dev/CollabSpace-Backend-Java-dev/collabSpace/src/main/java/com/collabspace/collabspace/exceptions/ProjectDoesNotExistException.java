package com.collabspace.collabspace.exceptions;

public class ProjectDoesNotExistException extends RuntimeException {
    public ProjectDoesNotExistException(String message) {
        super(message);
    }
}
