package com.collabspace.collabspace.dto;

import com.collabspace.collabspace.enums.ProjectStatus;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDate;
import java.util.UUID;

@Getter
@Setter
public class ProjectResponseDto {
    public UUID id;
    public String name;
    public String description;
    public LocalDate startDate;
    public LocalDate endDate;
    private ProjectStatus status;
    private UUID teamId;
    private UUID createdBy;
}
