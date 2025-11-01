// src/main/java/com/collabspace/collabspace/dto/TaskLinkDto.java
package com.collabspace.collabspace.dto;

import lombok.Getter;
import lombok.Setter;

import java.util.UUID;

@Getter
@Setter
public class TaskLinkDto {
    private UUID id;
    private String title;
    private String status;
}