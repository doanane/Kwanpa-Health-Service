package com.collabspace.collabspace.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.Setter;

import java.util.UUID;

@Getter
@Setter
public class SubtaskRequestDto {
    @NotNull(message = "Title field should not be empty")
    private String title;

    private String description;

    private UUID assigneeId;
}