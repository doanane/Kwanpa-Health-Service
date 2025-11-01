package com.collabspace.collabspace.services;

import com.collabspace.collabspace.dto.ProjectRequestDto;
import com.collabspace.collabspace.dto.ProjectResponseDto;
import com.collabspace.collabspace.entity.Project;
import com.collabspace.collabspace.entity.Team;
import com.collabspace.collabspace.repository.ProjectRepository;
import com.collabspace.collabspace.repository.TeamRepository;
import com.collabspace.collabspace.utils.ProjectValidator;
import jakarta.transaction.Transactional;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

import static com.collabspace.collabspace.utils.ProjectMapper.getProjectResponseDto;

@Service
@AllArgsConstructor
public class ProjectService {
    private final ProjectRepository projectRepository;
    private final TeamRepository teamRepository;
    private final ProjectValidator projectValidator;


    @Transactional
    public ProjectResponseDto createProject(ProjectRequestDto projectRequestDto, UUID createdBy) {
        //create a project
        Project project = new Project();
        project.setName(projectRequestDto.getName());
        project.setDescription(projectRequestDto.getDescription());
        project.setCreatedBy(createdBy);
        project.setStartDate(projectRequestDto.getStart_date());
        project.setEndDate(projectRequestDto.getEnd_date());

        //create the team
        Team team = new Team();
        team.setName(projectRequestDto.getName() + " Team");
        team.setCreatedBy(createdBy);
        Team savedTeam = teamRepository.save(team);
        project.setTeam(savedTeam);
        Project savedProject = projectRepository.save(project);
        return getProjectResponseDto(savedProject);
    }

    @Transactional
    public ProjectResponseDto updateProject(UUID projectId,ProjectRequestDto projectRequestDto, UUID createdBy) {
        Project project = projectValidator.ensureProjectExists(projectId);
        project.setName(projectRequestDto.getName());
        project.setDescription(projectRequestDto.getDescription());
        project.setStartDate(projectRequestDto.getStart_date());
        project.setEndDate(projectRequestDto.getEnd_date());
        Project savedProject = projectRepository.save(project);
        return getProjectResponseDto(savedProject);
    }


    public ProjectResponseDto getProjectById(UUID projectId) {
        Project project = projectValidator.ensureProjectExists(projectId);
        return getProjectResponseDto(project);
    }

    public Map<String, String> deleteProject(UUID projectId) {
        Project project = projectValidator.ensureProjectExists(projectId);
        projectRepository.deleteById(project.getId());
        Map<String, String> responseDto = new HashMap<>();
        responseDto.put("status", "success");
        responseDto.put("message", project.getName() +" has been deleted");
        return responseDto;
    }
}
