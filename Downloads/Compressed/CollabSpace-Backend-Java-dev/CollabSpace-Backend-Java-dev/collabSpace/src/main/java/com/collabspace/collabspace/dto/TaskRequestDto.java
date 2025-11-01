package com.collabspace.collabspace.dto;

import com.collabspace.collabspace.enums.Priority;
import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.Setter;

import java.util.Date;
import java.util.List;
import java.util.UUID;

@Getter
@Setter
public class TaskRequestDto {
    @NotNull(message = "Title field should not be empty")
    private String title;

    private String description;

    @NotNull(message = "Project ID field should not be empty")
    private UUID projectId;

    private UUID assigneeId;

    private Date dueDate;

    private Priority priority = Priority.MEDIUM;

    private List<UUID> linkedTaskIds;
}