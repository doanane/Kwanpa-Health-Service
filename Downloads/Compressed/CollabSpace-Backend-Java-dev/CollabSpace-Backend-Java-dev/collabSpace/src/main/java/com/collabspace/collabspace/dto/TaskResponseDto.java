package com.collabspace.collabspace.dto;

import com.collabspace.collabspace.enums.Priority;
import com.collabspace.collabspace.enums.TaskStatus;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDate;
import java.util.Date;
import java.util.List;
import java.util.UUID;

@Getter
@Setter
public class TaskResponseDto {
    private UUID id;
    private String title;
    private String description;
    private UUID projectId;
    private String projectName;
    private UUID assigneeId;
    private TaskStatus status;
    private Priority priority;
    private Date dueDate;
    private LocalDate createdAt;
    private List<SubtaskResponseDto> subtasks;
    private List<TaskLinkDto> linkedWorkItems;
}