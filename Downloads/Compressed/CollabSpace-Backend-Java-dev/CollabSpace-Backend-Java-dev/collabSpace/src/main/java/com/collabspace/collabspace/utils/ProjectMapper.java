package com.collabspace.collabspace.utils;

import com.collabspace.collabspace.dto.ProjectResponseDto;
import com.collabspace.collabspace.entity.Project;
import com.collabspace.collabspace.repository.ProjectRepository;

public class ProjectMapper {
    private static ProjectRepository projectRepository;
    public static ProjectResponseDto getProjectResponseDto(Project savedProject) {
        ProjectResponseDto responseDto = new ProjectResponseDto();
        responseDto.setId(savedProject.getId());
        responseDto.setName(savedProject.getName());
        responseDto.setDescription(savedProject.getDescription());
        responseDto.setCreatedBy(savedProject.getCreatedBy());
        responseDto.setStartDate(savedProject.getStartDate());
        responseDto.setEndDate(savedProject.getEndDate());
        responseDto.setTeamId(savedProject.getTeam().getId());
        responseDto.setStatus(savedProject.getStatus());
        return responseDto;
    }
}
