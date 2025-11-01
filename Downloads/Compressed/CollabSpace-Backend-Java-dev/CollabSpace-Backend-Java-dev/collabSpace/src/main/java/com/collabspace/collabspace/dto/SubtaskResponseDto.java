package com.collabspace.collabspace.dto;

import com.collabspace.collabspace.enums.TaskStatus;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDate;
import java.util.UUID;

@Getter
@Setter
public class SubtaskResponseDto {
    private UUID id;
    private String title;
    private String description;
    private UUID parentTaskId;
    private UUID assigneeId;
    private TaskStatus status;
    private LocalDate createdAt;
}