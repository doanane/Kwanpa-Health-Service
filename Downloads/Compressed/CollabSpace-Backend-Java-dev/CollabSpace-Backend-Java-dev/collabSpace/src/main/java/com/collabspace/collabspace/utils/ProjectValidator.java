package com.collabspace.collabspace.utils;

import com.collabspace.collabspace.entity.Project;
import com.collabspace.collabspace.exceptions.ProjectDoesNotExistException;
import com.collabspace.collabspace.repository.ProjectRepository;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Component;

import java.util.UUID;

@Component
@AllArgsConstructor
public class ProjectValidator {

    private final ProjectRepository projectRepository;

    public Project ensureProjectExists(UUID projectId) {
        return projectRepository.findById(projectId)
                .orElseThrow(() -> new ProjectDoesNotExistException("Project does not exist"));
    }
}
